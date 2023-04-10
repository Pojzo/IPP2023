from input_handler import ArgumentType
from error_codes import ErrorCodes
from debug import DEBUG_PRINT
from config import DEBUG
from instructions import DataType


class Frame:
    def __init__(self):
        self.variables: set = {}

    # get the value of a variable or exit with error if the variable doesn't exist
    def get(self, name: str) -> str:
        if name in self.variables:
            return self.variables[name]
        else:
            DEBUG_PRINT("Variable {} not found in frame".format(name))
            exit(ErrorCodes.VariableNotDefined)

    
    # define variable with None or exit with error if its aleady defined
    def define(self, name: str) -> None:
        if name in self.variables:
            DEBUG_PRINT("Variable {} not found in frame".format(name))
            exit(ErrorCodes.VariableRedefinition)

        self.variables[name] = None

    # set the value of a variable or exit with error
    def set(self, name: str, value: str) -> None:
        if not name in self.variables:
            DEBUG_PRINT("Variable {} not found in frame".format(name))
            exit(ErrorCodes.VariableNotDefined)

        self.variables[name] = value


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# Memory is resposible for handling all the frames
class Memory(metaclass=Singleton):
    def __init__(self):
        self._global_frame = Frame()
        self._temporary_frame = None
        self._stack = []
    
    
    # ///--------- DEFINING VARIABLES IN FRAMES -------\\\\\\

    # define a local variable
    def _define_local(self, name: str) -> None:
        # check if there is any frame at all
        if len(self._stack) == 0:
            exit(ErrorCodes.FrameNotDefined)

        local_frame = self._stack[-1]

        local_frame.define(name)

    # define a variable in the temporary frame
    def _define_temporary(self, name: str) -> None:
        if self._temporary_frame == None: 
            self._temporary_frame = Frame()

        self._temporary_frame.define(name)
        print("Tu som sa mal dostat", name)

    # define a variable in the global frame
    def _define_global(self, name: str) -> None:
        self._global_frame.define(name)

    def define_var(self, name: str, frame: str):
        assert(frame in ["GF", "LF", "TF"])
        {'GF': self._define_global,
         'LF': self._define_local,
         'TF': self._define_temporary}[frame](name)

    # create a new temporary frame
    # discard the old one if it exists
    def create_frame(self) -> None:
        self._temporary_frame = Frame()

    # push temporary frame onto the stack
    def push_frame(self) -> None:
        if self._temporary_frame == None:
            DEBUG_PRINT("Temporary frame doesn't exist")
            exit(ErrorCodes.FrameNotDefined)
        
        self._stack.append(self._temporary_frame)

        # reset temporary frame 
        self._temporary_frame = None

    # pop local frame into the temporary frame
    def pop_frame(self) -> None:
        # check if there's a local frame
        if len(self._stack) == 0:
            DEBUG_PRINT("Local frame doesn't exist")
            exit(ErrorCodes.FrameNotDefined)
        
        if self._temporary_frame != None:
            del self._temporary_frame

        self._temporary_frame = self._stack.pop(-1)

    # testing function
    def get_stack(self) -> list[Frame]:
        return self._stack

    def get_global_frame(self) -> Frame:
        return self._global_frame

