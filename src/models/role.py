from enum import Enum, unique


@unique
class UserRole(int, Enum):
    BANNED = 1
    USER = 2
    ADMIN = 3
    GUEST = 4
