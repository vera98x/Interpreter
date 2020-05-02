from enum import Enum

class Errornr(Enum):
    NO_ERROR = 0
    SYNTAX_ERROR = 1
    FileNotFoundError = 2

class Error():
    def __init__(self, errornr, errormsg = ""):
        self.nr = errornr
        self.msg = errormsg

    def __str__(self):
        return (str(self.nr) + ": " + self.msg)

    def __repr__(self):
        return self.__str__()

class State(Enum):
    Idle = 0
    Math = 1
    IF = 2
    IF_CONDITION = 3
    IF_BLOCK = 4
    ASSIGN = 6
    DONE = 7
    WHILE = 8
    WHILE_CONDITION = 9
    WHILE_BLOCK = 10
    COMPARISON = 11