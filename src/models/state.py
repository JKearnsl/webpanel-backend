from enum import Enum, unique


@unique
class UserStates(int, Enum):
    NOT_CONFIRMED = 1
    ACTIVE = 2
    DELETED = 3
