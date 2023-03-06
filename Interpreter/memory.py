from input_handler import ArgumentType
from error_codes import ErrorCodes
from config import DEBUG

# creat enum for data types
class DataType(Enum):
     int = 1
     string = 2
     bool = 3
     nil = 4

class Frame:
    def __init__(self):
        self.variables = {}

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        else:
            if DEBUG:
                print("Variable {} not found in frame".format(name))
            exit(ErrorCodes.VariableNotDefined)

    def set(self, name, value):
        self.variables[name] = value


# Memory is resposible for handling all the frames
class Memory:
    def __init__(self):
        self.global_frame = Frame()
        self.local_frame = None
        self.temporary_frame = None
        self.stack = []

    var define(self, arg_type_: ArgumentType, name: str, value: str):
        self.global_frame.set(name, value)
