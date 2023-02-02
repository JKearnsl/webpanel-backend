from starlette.authentication import AuthCredentials, UnauthenticatedUser, BaseUser
from starlette.middleware.base import BaseHTTPMiddleware

from fastapi.requests import Request
from starlette.middleware.exceptions import ExceptionMiddleware

from src.models.role import UserRole
from src.models.state import UserStates
from src.models import schemas
from src.services.auth import JWTManager
from src.services.auth import SessionManager
from src.services.repository import UserRepo


class JWTMiddleware(BaseHTTPMiddleware):

    def __init__(self, app: ExceptionMiddleware):
        super().__init__(app)

        self.debug = app.debug

    async def dispatch(self, request: Request, call_next):
        jwt = JWTManager(config=request.app.state.config, debug=self.debug)
        session = SessionManager(redis_client=request.app.state.redis, debug=self.debug,config=request.app.state.config)
        db_session = request.app.state.db_session

        session_id = session.get_session_id(request)
        current_tokens = jwt.get_jwt_cookie(request)
        is_need_update = False
        is_auth = False

        # ----- pre_process -----
        # Проверка авторизации
        if current_tokens:
            is_valid_access_token = jwt.is_valid_access_token(current_tokens.access_token)
            is_valid_refresh_token = jwt.is_valid_refresh_token(current_tokens.refresh_token)
            is_valid_session = False

            if is_valid_refresh_token:
                # Проверка валидности сессии
                if await session.is_valid_session(session_id, current_tokens.refresh_token):
                    is_valid_session = True

            is_auth = is_valid_access_token and is_valid_refresh_token and is_valid_session
            is_need_update = (not is_valid_access_token) and is_valid_refresh_token and is_valid_session

        # Обновление токенов
        if is_need_update:
            user_id = jwt.decode_refresh_token(current_tokens.refresh_token).id
            async with db_session() as active_session:
                user = await UserRepo(active_session).get(id=user_id)

            if user:
                new_tokens = jwt.generate_tokens(
                    id=user.id,
                    username=user.username,
                    role_value=user.role.value,
                    state_value=user.state.value
                )
                # Для бесшовного обновления токенов:
                request.cookies["access_token"] = new_tokens.access_token
                request.cookies["refresh_token"] = new_tokens.refresh_token
                current_tokens = new_tokens
                is_auth = True

        # Установка данных авторизации
        if is_auth:
            payload: schemas.TokenPayload = jwt.decode_access_token(current_tokens.access_token)
            request.scope["user"] = AuthenticatedUser(**payload.dict())
            request.scope["auth"] = AuthCredentials(["authenticated"])
        else:
            request.scope["user"] = UnauthenticatedUser()
            request.scope["auth"] = AuthCredentials()

        response = await call_next(request)

        # ----- post_process -----
        if is_need_update:
            # Обновляем response
            jwt.set_jwt_cookie(response, current_tokens)
            await session.set_session_id(response, current_tokens.refresh_token, session_id)

        return response


class AuthenticatedUser(BaseUser):
    def __init__(self, id: int, username: str, role_value: int, state_value: int, **kwargs):
        self._id = id
        self._username = username
        self._role_value = role_value
        self._state_value = state_value

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def identity(self) -> int:
        return self._id

    @property
    def id(self) -> int:
        return self._id

    @property
    def username(self) -> str:
        return self.username

    @property
    def role(self) -> UserRole:
        return UserRole(self._role_value)

    @property
    def state(self) -> UserStates:
        return UserStates(self._state_value)

    def __eq__(self, other):
        return isinstance(other, AuthenticatedUser) and self._id == other.id

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self._id}, username={self._username})>"
