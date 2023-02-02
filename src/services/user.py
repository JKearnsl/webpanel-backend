from typing import Optional, Union

from starlette.authentication import UnauthenticatedUser


from src import views
from src.exceptions import AccessDenied, NotFound
from src.models import tables, schemas
from src.models.role import UserRole
from src.services.auth.utils import auth
from src.services.repository import UserRepo


class UserApplicationService:

    def __init__(self, user_repo: UserRepo, *, current_user: Optional[tables.User], debug: bool = False):
        self._repo = user_repo
        self._current_user: 'AuthenticatedUser' | UnauthenticatedUser = current_user
        self._debug = debug

    @auth(is_authenticated=True)
    async def get_me(self) -> Optional[views.user.UserBigResponse]:
        """
        Get UserBigResponse
        """
        return await self._repo.get(id=self._current_user.id)

    async def get_user(self, user_id: int) -> Union[views.user.UserSmallResponse, views.user.UserBigResponse]:
        """
        Get user by id # todo: by all fields
        """
        user = await self._repo.get(id=user_id)

        if not user:
            raise NotFound(f"User with id {user_id} not found")

        if self._current_user.is_authenticated and self._current_user.role == UserRole.ADMIN:
            return views.user.UserBigResponse.from_orm(user)
        elif self._current_user.is_authenticated and self._current_user.id == user_id:
            return views.user.UserBigResponse.from_orm(user)
        else:
            return views.user.UserSmallResponse.from_orm(user)
        # todo: check parser

    @auth(is_authenticated=True)
    async def update_user(self, user_id: int, **kwargs) -> None:
        """
        Update user by id
        """

        if self._current_user.id != user_id and self._current_user.role != UserRole.ADMIN:
            raise AccessDenied("You can't update other user")

        if self._current_user.id == user_id:
            return await self._repo.update(id=user_id, **kwargs)  # todo: remove kwargs

        return await self._repo.update(id=user_id, **kwargs)  # TODO: debug this

    @auth(is_authenticated=True)
    async def update_me(self, **kwargs) -> None:
        """
        Update me
        """
        return await self._repo.update(id=self._current_user.id, **kwargs)  # TODO: debug this

    @auth(is_authenticated=True)
    async def delete_user(self, user_id: int) -> None:
        """
        Delete user by id
        """

        if self._current_user.id != user_id and self._current_user.role != UserRole.ADMIN:
            raise AccessDenied("You can't delete other user")

        await self._repo.delete(id=user_id)
