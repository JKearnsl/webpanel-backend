import typing
from fastapi.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.websockets import WebSocket


class APIError(Exception):
    def __init__(
            self,
            message: str = "Error",
            status_code: int = 400,
            headers: typing.Optional[dict] = None
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.headers = headers


class AccessDenied(APIError):
    status_code = 403
    message = "Access denied"

    def __init__(self, message: str = None) -> None:
        super().__init__(message=message if message else self.message, status_code=403)


class NotFound(APIError):
    status_code = 404
    message = "Not Found"

    def __init__(self, message: str = None) -> None:
        super().__init__(message=message if message else self.message, status_code=404)


class AlreadyExists(APIError):
    status_code = 409
    message = "Already exists"

    def __init__(self, message: str = None) -> None:
        super().__init__(message=message if message else self.message, status_code=409)


async def handle_api_error(request, exc):
    if isinstance(request, WebSocket):
        await request.accept()
        await request.close(code=int(f'{exc.status_code}0'), reason=exc.message)
        return
    else:
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message},
        )


async def handle_pydantic_error(request, exc: ValidationError):
    return JSONResponse(  # todo: parse it
        status_code=400,
        content={"message": exc.errors()},
    )


async def handle_404_error(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Not Found"},
    )
