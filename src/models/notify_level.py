from enum import Enum, unique


@unique
class NotifyLevel(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3
