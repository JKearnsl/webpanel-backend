import time
from functools import wraps
from typing import Union

from src.exceptions import AccessDenied
from src.models.role import UserRole


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')


def filters(
        roles: Union[list[UserRole], UserRole] = None,
):
    """
    Role Filter decorator for ApplicationServices

    It is necessary that the class of the method being decorated has a field '_current_user'

    :param roles: user role
    :return: decorator
    """

    if roles is None:
        roles = [role for role in UserRole]
    if not isinstance(roles, list):
        roles = list().append(roles)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            service_class: object = args[0]
            current_user = service_class.__getattribute__('_current_user')
            if not current_user:
                raise ValueError('AuthMiddleware not found')

            # Access exp check
            if current_user.role == UserRole.GUEST and current_user.access_exp:
                if current_user.access_exp < time.time():
                    raise AccessDenied('Access token expired')
                # TODO: подумать о ситуациях, когда пользователь может подменить токены: refresh, access
                raise RuntimeError('Access token dont expired, but user role=GUEST; access_exp not None')

            if current_user.role in roles:
                return await func(*args, **kwargs)
            else:
                raise AccessDenied('User has no access')

        return wrapper

    return decorator
