"""Application implementation - ASGI."""
import logging

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from pydantic import ValidationError

from src.models import tables
from src.db import create_sqlite_async_session
from src.middleware import JWTMiddlewareHTTP, JWTMiddlewareWS
from src.config import load_ini_config
from src.exceptions import APIError, handle_api_error, handle_404_error, handle_pydantic_error

from src.router import reg_root_api_router
from src.services.stats import stat_worker
from src.utils import RedisClient, AiohttpClient
from src.utils.bgmanager import BGManager
from src.utils.wsmanager import WSConnectionManager, WSJWTConnectionManager

config = load_ini_config('./config.ini')
log = logging.getLogger(__name__)

log.debug("Инициализация приложения FastAPI.")
app = FastAPI(
    title=config.BASE.TITLE,
    debug=config.DEBUG,
    version=config.BASE.VERSION,
    description=config.BASE.DESCRIPTION,
    root_path="/api/v1" if not config.DEBUG else "",
    docs_url="/api/docs" if config.DEBUG else "/docs",
    redoc_url="/api/redoc" if config.DEBUG else "/redoc",
    contact={
        "name": config.BASE.CONTACT.NAME,
        "url": config.BASE.CONTACT.URL,
        "email": config.BASE.CONTACT.EMAIL,
    }
)


async def init_sqlite_db():
    engine, session = create_sqlite_async_session(
        database='database.db',
        echo=config.DEBUG,
    )
    app.state.db_session = session

    async with engine.begin() as conn:
        # await conn.run_sync(tables.Base.metadata.drop_all)
        await conn.run_sync(tables.Base.metadata.create_all)


async def redis_pool(db: int = 0):
    return await redis.from_url(
        f"redis://:{config.DB.REDIS.PASSWORD}@{config.DB.REDIS.HOST}:{config.DB.REDIS.PORT}/{db}",
        encoding="utf-8",
        decode_responses=True,
    )


async def init_background_manager():
    app.state.background_manager = BGManager()
    app.state.background_manager.add_job(
        stat_worker, 'interval', seconds=3, args=(app,)
    )
    app.state.background_manager.start()


@app.on_event("startup")
async def on_startup():
    log.debug("Executing FastAPI startup event handler.")
    # Initialize utilities.
    app.state.notifier_ws = WSConnectionManager()
    app.state.stats_ws = WSJWTConnectionManager()
    app.state.redis = RedisClient(await redis_pool())
    app.state.http_client = AiohttpClient()

    await init_sqlite_db()
    await init_background_manager()


@app.on_event("shutdown")
async def on_shutdown():
    log.debug("Executing FastAPI shutdown event handler.")
    # Gracefully close utilities.
    await app.state.redis.close()
    await app.state.http_client.close_session()


# custom OpenApi # todo: move to other fold
def custom_openapi():
    if not app.openapi_schema:
        app.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            terms_of_service=app.terms_of_service,
            contact=app.contact,
            license_info=app.license_info,
            routes=app.routes,
            tags=app.openapi_tags,
            servers=app.servers,
        )
        for _, method_item in app.openapi_schema.get('paths').items():
            for _, param in method_item.items():
                responses = param.get('responses')
                # remove 422 response, also can remove other status code
                if '422' in responses:
                    del responses['422']
    return app.openapi_schema


app.openapi = custom_openapi
app.state.config = config

log.debug("Adding routers.")
app.include_router(reg_root_api_router(config.DEBUG))
log.debug("Registering exception handlers.")
app.add_exception_handler(APIError, handle_api_error)
app.add_exception_handler(404, handle_404_error)
app.add_exception_handler(ValidationError, handle_pydantic_error)
app.add_exception_handler(RequestValidationError, handle_pydantic_error)  # todo: dont work
log.debug("Registering middleware.")
app.add_middleware(JWTMiddlewareHTTP)
app.add_middleware(JWTMiddlewareWS)
