import typing
from fastapi.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class APIError(StarletteHTTPException):
    def __init__(
            self,
            message: str = "Error",
            status_code: int = 400,
            headers: typing.Optional[dict] = None
    ) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(status_code=status_code, headers=headers)


class AccessDenied(APIError):
    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(message=message, status_code=403)


class NotFound(APIError):
    def __init__(self, message: str = "Not Found") -> None:
        super().__init__(message=message, status_code=404)


class AlreadyExists(APIError):
    def __init__(self, message: str = "Already exists") -> None:
        super().__init__(message=message, status_code=409)


async def handle_api_error(request, exc):
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