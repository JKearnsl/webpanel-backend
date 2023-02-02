from enum import Enum, unique


@unique
class UserRole(int, Enum):
    BANNED = 1
    USER = 2
    MODERATOR = 3
    ADMINISTRATOR = 4
