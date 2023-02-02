from src.exceptions import NotFound
from src.models import schemas
from src.services.auth.password import get_hashed_password
from src.services.repository import UserRepo


class InitialApplicationService:

    def __init__(self, user_repo: UserRepo):
        self._user_repo = user_repo

    async def create_start_user(self, user: schemas.UserSignUp) -> schemas.User:
        """
        Создание стартового пользователя
        """
        count_of_users = await self._user_repo.count()
        if count_of_users > 0:
            raise NotFound()

        hashed_password = get_hashed_password(user.password)
        return await self._user_repo.create(**user.dict(exclude={"password"}), hashed_password=hashed_password)
