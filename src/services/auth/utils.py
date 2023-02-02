from functools import wraps

from src.exceptions import AccessDenied
from src.models.state import UserStates
from src.models.role import UserRole


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')


def auth(
        is_authenticated: bool = True,
        *,
        is_admin: bool = True,
        is_moderator: bool = True,
        is_user: bool = True,
        state: UserStates = UserStates.ACTIVE,
):
    """
    Authenticate user decorator for ApplicationService

    It is necessary that the class of the method being decorated has a field '_current_user'

    :param is_authenticated: is user authenticated
    :param is_admin: is user admin
    :param is_moderator: is user moderator
    :param is_user: is user user
    :param state: user state
    :return: decorator
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            service_class: object = args[0]
            current_user = service_class.__getattribute__('_current_user')
            if not is_authenticated:
                if current_user.is_authenticated:
                    raise AccessDenied('User is authenticated')
                return await func(*args, **kwargs)

            if is_authenticated and current_user.is_authenticated is False:
                raise AccessDenied('User is not authenticated')

            if current_user.state != state:
                raise AccessDenied('User has no access')

            inc = set()
            if is_admin:
                inc.add(UserRole.ADMINISTRATOR)
            if is_moderator:
                inc.add(UserRole.MODERATOR)
            if is_user:
                inc.add(UserRole.USER)

            if current_user.role not in inc:
                raise AccessDenied('User has no access')

            return await func(*args, **kwargs)

        return wrapper

    return decorator
