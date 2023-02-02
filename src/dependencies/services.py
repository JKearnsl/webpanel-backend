from fastapi import Depends
from fastapi.requests import Request

from src.dependencies.repos import get_repos
from src.services import ServiceFactory
from src.services.repository import RepoFactory


async def get_services(request: Request, repos: RepoFactory = Depends(get_repos)) -> ServiceFactory:
    yield ServiceFactory(
        repos,
        current_user=request.scope.get("user"),
        config=request.app.state.config,
        redis_client=request.app.state.redis,
        debug=request.app.state.config.DEBUG,
    )
