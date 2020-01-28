from enum import Enum


class CMD_STATE(Enum):
    Undefined = ' '
    Ask = '+'
    In_Progress = 'o'
    Get = '-'
