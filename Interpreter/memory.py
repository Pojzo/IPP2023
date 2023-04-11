from input_handler import ArgumentType

from error_codes import ErrorCodes
from debug import DEBUG_PRINT
from config import DEBUG
from instructions import DataType
from instructions import Variable

       

class Frame:
    def __init__(self):
        self.variables: set[Variable] = {}

    # get the value of a variable or exit with error if the variable doesn't exist
    def get(self, name: str) -> str:
        if name in self.variables:
            return self.variables[name]
        else:
            return None


    # define variable with None or exit with error if its aleady defined
    def define(self, name: str) -> None:
        if name in self.variables:
            DEBUG_PRINT("Variable {} not found in frame".format(name))
            exit(ErrorCodes.VariableRedefinition)

        self.variables[name] = Variable(name)

    # set the value of a variable or exit with error
    def set(self, name: str, value: str, type_: type) -> None:
        if not name in self.variables:
            DEBUG_PRINT("Variable {} not found in frame".format(name))
            exit(ErrorCodes.VariableNotDefined)

        self.variables[name].value = value
        self.variables[name].type_ = type_


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
        self._frame_stack = []
        self._data_stack = []
    
    
    # ///--------- DEFINING VARIABLES IN FRAMES -------\\\\\\

    # define a local variable
    def _define_local(self, name: str) -> None:
        # check if there is any frame at all
        if len(self._frame_stack) == 0:
            exit(ErrorCodes.FrameNotDefined)

        local_frame = self._frame_stack[-1]

        local_frame.define(name)

    # define a variable in the temporary frame
    def _define_temporary(self, name: str) -> None:
        if self._temporary_frame == None: 
            self._temporary_frame = Frame()

        self._temporary_frame.define(name)

    # define a variable in the global frame
    def _define_global(self, name: str) -> None:
        self._global_frame.define(name)

    def define_var(self, name: str, frame: str):
        assert(frame in ["GF", "LF", "TF"])
        {'GF': self._define_global,
         'LF': self._define_local,
         'TF': self._define_temporary}[frame](name)

    
    # ///--------- FUNCTIONS WITH FRAME STACK -------\\\\\\

    # create a new temporary frame
    # discard the old one if it exists
    def create_frame(self) -> None:
        self._temporary_frame = Frame()

    # push temporary frame onto the stack
    def push_frame(self) -> None:
        if self._temporary_frame == None:
            DEBUG_PRINT("Temporary frame doesn't exist")
            exit(ErrorCodes.FrameNotDefined)
        
        self._frame_stack.append(self._temporary_frame)

        # reset temporary frame 
        self._temporary_frame = None
    
    # pop local frame into the temporary frame
    def pop_frame(self) -> None:
        # check if there's a local frame
        if len(self._frame_stack) == 0:
            DEBUG_PRINT("Local frame doesn't exist")
            exit(ErrorCodes.FrameNotDefined)
        
        if self._temporary_frame != None:
            del self._temporary_frame

        self._temporary_frame = self._frame_stack.pop(-1)
    
    # return variable in global frame
    def _global_get_var(self, name: str) -> Variable:
        return self._global_frame.get(name)

    # return variable in local frame
    def _local_get_var(self, name: str) -> Variable:
        if len(self._frame_stack) == 0:        
            DEBUG_PRINT(f"Local frame doesn't exist")
            exit(ErrorCodes.FrameNotDefined)
        
        local_frame = self._frame_stack[-1]
        var = local_frame.get(name)
        return var

    def _temporary_get_var(self, name: str) -> Variable:
        if self._temporary_frame is None:
            DEBUG_PRINT(f"Temporary frame doesn't exist")
            exit(ErrorCodes.FrameNotDefined)

        var = self._temporary_frame.get(name)
        return var


    def get_var(self, name: str, frame: str) -> str:
        var =  {'GF': self._global_get_var,
                'LF': self._local_get_var,
                'TF': self._temporary_get_var}[frame](name)

        if var is None:
            DEBUG_PRINT(f"Variable {name} not defined in {frame}")
            exit(ErrorCodes.VariableNotDefined)

        return var
    
    # move var value from source to dest
    def move_var(self, source_name: str, source_frame: str, dest_name: str, dest_frame: str) -> None:
        source_var = self.get_var(source_name, source_frame)
        dest_var = self.get_var(dest_name, dest_frame)
        dest_var.value = source_var.value
        dest_var.datatype = source_var.datatype

    
    def set_var(self, name: str, frame: str, value: str, datatype: DataType) -> None:
        var = self.get_var(name, frame)
        var.value = value
        var.datatype = datatype
    

    # the operands will be on the stack
    def add(self, dest_name, dest_frame) -> None:
        first_operand = self.pop_data()
        second_operand = self.pop_data()
        if first_operand.datatype != second_operand.datatype:
            DEBUG_PRINT("ADD datatypes not matching")
            exit(ErrorCodes.OperandValueBad)

        source_var = self.get_var(dest_name, dest_frame)
        source_var.value = int(first_operand.value) + int(second_operand.value)

    
    # testing function
    def get_frame_stack(self) -> list[Frame]:
        return self._frame_stack
    
    def get_global_frame(self) -> Frame:
        return self._global_frame
    
    # ///--------- FUNCTIONS WITH DATA STACK -------\\\\\\ 

    # push data on top of the data stack
    def push_data(self, value: str, datatype: DataType) -> None:
        # "stack_var" is default name for stack variables - they can be anonymous
        new_var = Variable("stack_var")
        new_var.value = value
        new_var.datatype = datatype
        self._data_stack.append(new_var)

    # pop data from the top of the data stack

    def pop_data(self) -> str:
        if len(self._data_stack) == 0:
            DEBUG_PRINT("Data stack is empty")
            exit(ErrorCodes.DataStackEmpty)

        return self._data_stack.pop(-1)

