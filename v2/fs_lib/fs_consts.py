from enum import Enum

class FS_Flag(Enum):
    SUCCESS = 0
    FAILED = 1
    FINISHED = 2
    RESET = 3

class FS_Type(Enum):
    MESSAGE = 0
    FILE = 1