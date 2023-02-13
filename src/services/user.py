from typing import Optional, Union


from src import views
from src.exceptions import AccessDenied, NotFound
from src.models import tables
from src.models.role import UserRole
from src.services.auth.utils import filters
from src.services.repository import UserRepo


class UserApplicationService:

    def __init__(self, user_repo: UserRepo, *, current_user: Optional[tables.User], debug: bool = False):
        self._repo = user_repo
        self._current_user = current_user
        self._debug = debug

    @filters(roles=[UserRole.ADMIN, UserRole.USER])
    async def get_me(self) -> Optional[views.user.UserBigResponse]:
        """
        Get UserBigResponse
        """
        return await self._repo.get(id=self._current_user.id)

    @filters(roles=[UserRole.ADMIN, UserRole.USER])
    async def get_user(self, user_id: int) -> Union[views.user.UserSmallResponse, views.user.UserBigResponse]:
        """
        Get user by id # todo: by all fields
        """
        user = await self._repo.get(id=user_id)

        if not user:
            raise NotFound(f"User with id {user_id} not found")

        if self._current_user.role == UserRole.ADMIN:
            return views.user.UserBigResponse.from_orm(user)
        else:
            return views.user.UserSmallResponse.from_orm(user)

    @filters(roles=[UserRole.ADMIN, UserRole.USER])
    async def update_user(
            self,
            user_id: int,
            *,
            username: Optional[str] = None,
            email: Optional[str] = None,
            role: Optional[UserRole] = None,
    ) -> None:
        """
        Update user by id
        """

        if self._current_user.id != user_id and self._current_user.role != UserRole.ADMIN:
            raise AccessDenied("You can't update other user")
        elif self._current_user.id == user_id and self._current_user.role != UserRole.ADMIN:
            return await self._repo.update(
                id=user_id,
                **{'username': username} if username else {},
                **{'email': email} if email else {},
            )
        return await self._repo.update(
            id=user_id,
            **{'username': username} if username else {},
            **{'email': email} if email else {},
            **{'role': role} if role else {},
        )

    @filters(roles=[UserRole.ADMIN, UserRole.USER])
    async def update_me(self, **kwargs) -> None:
        """
        Update me
        """
        return await self.update_user(self._current_user.id, **kwargs)

    @filters(roles=[UserRole.ADMIN])
    async def delete_user(self, user_id: int) -> None:
        """
        Delete user by id
        """

        if self._current_user.id == user_id:
            raise AccessDenied("You can't delete yourself")

        await self._repo.delete(id=user_id)
