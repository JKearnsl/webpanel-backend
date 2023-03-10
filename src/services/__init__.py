from src.models import tables
from . import repository
from . import auth
from .info import InfoApplicationService
from .initial import InitialApplicationService
from .stats import StatsApplicationService
from .user import UserApplicationService


class ServiceFactory:
    def __init__(
            self,
            repo_factory: repository.RepoFactory,
            *,
            current_user: tables.User,
            config, redis_client,
            stats_ws_manager,
            notify_ws_manager,
            debug: bool = False
    ):
        self._repo = repo_factory
        self._current_user = current_user
        self._config = config
        self._redis_client = redis_client
        self._stats_ws_manager = stats_ws_manager
        self._notify_ws_manager = notify_ws_manager
        self._debug = debug

    @property
    def user(self) -> UserApplicationService:
        return UserApplicationService(self._repo.user, current_user=self._current_user, debug=self._debug)

    @property
    def auth(self) -> auth.AuthApplicationService:
        return auth.AuthApplicationService(
            jwt=auth.JWTManager(config=self._config, debug=self._debug),
            session=auth.SessionManager(redis_client=self._redis_client, config=self._config, debug=self._debug),
            user_repo=self._repo.user,
            current_user=self._current_user,
            debug=self._debug
        )

    @property
    def initial(self) -> InitialApplicationService:
        return InitialApplicationService(self._repo.user)

    @property
    def info(self) -> InfoApplicationService:
        return InfoApplicationService(config=self._config, current_user=self._current_user)

    @property
    def stats(self) -> StatsApplicationService:
        return StatsApplicationService(stats_ws_manager=self._stats_ws_manager, current_user=self._current_user)
