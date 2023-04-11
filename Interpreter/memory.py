from input_handler import ArgumentType

from error_codes import ErrorCodes
from debug import DEBUG_PRINT
from config import DEBUG
from instructions import DataType
from instructions import Variable


def convert_string_to_bool(string: str) -> bool:
    if string.lower() == "true":
        return True
    return False


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
    def _local_define(self, name: str) -> None:
        # check if there is any frame at all
        if len(self._frame_stack) == 0:
            exit(ErrorCodes.FrameNotDefined)

        local_frame = self._frame_stack[-1]

        local_frame.define(name)

    # define a variable in the temporary frame
    def _temporary_define(self, name: str) -> None:
        if self._temporary_frame == None: 
            DEBUG_PRINT("Temporary frame doesn't exist")
            exit(ErrorCodes.FrameNotDefined)

        self._temporary_frame.define(name)

    # define a variable in the global frame
    def _global_define(self, name: str) -> None:
        self._global_frame.define(name)

    def define_var(self, name: str, frame: str):
        assert(frame in ["GF", "LF", "TF"])
        {'GF': self._global_define,
         'LF': self._local_define,
         'TF': self._temporary_define}[frame](name)

    
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
    
    
    def _check_type(self, type_: DataType, allowed_types: list[DataType]) -> None:
        if type_ not in allowed_types:
            DEBUG_PRINT("Instruction wrong datatype")
            exit(ErrorCodes.OperandTypeBad)

    def _check_matching_operands(self, operand1_datatype: DataType, operand2_datatype: DataType) -> None:
        if operand1_datatype != operand2_datatype:
            DEBUG_PRINT("ADD datatypes not matching"+ str(operand1_datatype) + "/" + str(operand2_datatype))
            exit(ErrorCodes.OperandTypeBad)


    def add(self, dest_name: str, dest_frame: str) -> None:
        first_operand = self.pop_data()
        second_operand = self.pop_data()
        self._check_type(first_operand.datatype, [DataType.TYPE_INT, DataType.TYPE_FLOAT])
        self._check_matching_operands(first_operand.datatype, second_operand.datatype)

        source_var = self.get_var(dest_name, dest_frame)
        source_var.value = str(int(first_operand.value) + int(second_operand.value))
        source_var.datatype = first_operand.datatype

    def sub(self, dest_name: str, dest_frame: str) -> None:
        first_operand = self.pop_data()
        second_operand = self.pop_data()
        self._check_type(first_operand.datatype, [DataType.TYPE_INT, DataType.TYPE_FLOAT])
        self._check_matching_operands(first_operand.datatype, second_operand.datatype)

        source_var = self.get_var(dest_name, dest_frame)
        source_var.value = str(int(first_operand.value) - int(second_operand.value))
        source_var.datatype = first_operand.datatype

    def mul(self, dest_name: str, dest_frame: str) -> None:
        first_operand = self.pop_data()
        second_operand = self.pop_data()
        self._check_type(first_operand.datatype, [DataType.TYPE_INT, DataType.TYPE_FLOAT])
        self._check_matching_operands(first_operand.datatype, second_operand.datatype)

        source_var = self.get_var(dest_name, dest_frame)
        source_var.value = str(int(first_operand.value) * int(second_operand.value))
        source_var.datatype = first_operand.datatype

    def idiv(self, dest_name: str, dest_frame: str) -> None:
        first_operand = self.pop_data()
        second_operand = self.pop_data()
        self._check_type(first_operand.datatype, [DataType.TYPE_INT, DataType.TYPE_FLOAT])
        self._check_matching_operands(first_operand.datatype, second_operand.datatype)
       
        source_var = self.get_var(dest_name, dest_frame)
        try:
            source_var.value = str(int(first_operand.value) / int(second_operand.value))
        except ZeroDivisionError:
            DEBUG_PRINT("IDIV by zero")
            exit(ErrorCodes.OperandValueBad)
    
        source_var.datatype = first_operand.datatype


    def lt(self, dest_name: str, dest_frame: str) -> None:
        first_operand = self.pop_data()
        second_operand = self.pop_data()
        self._check_matching_operands(first_operand.datatype, second_operand.datatype)
        self._check_type(first_operand.datatype, [DataType.TYPE_INT, DataType.TYPE_STRING, DataType.TYPE_BOOL,
                         DataType.TYPE_FLOAT])
        
        source_var = self.get_var(dest_name, dest_frame)
        if first_operand.datatype == DataType.TYPE_INT:
            result = "true" if int(first_operand.value) < int(second_operand.value) else "false"

        if first_operand.datatype == DataType.TYPE_FLOAT:
            result = "true" if float(first_operand.value) < float(second_operand.value) else "false"

        if first_operand.datatype == DataType.TYPE_BOOL:
            result = "true" if convert_string_to_bool(first_operand.value) < convert_string_to_bool(second_operand.value) else "false"

        if first_operand.datatype == DataType.TYPE_STRING:
            result = "true" if first_operand.value < second_operand.value else "false"


        source_var.datatype = DataType.TYPE_BOOL
        source_var.value = result

    def gt(self, dest_name: str, dest_frame: str) -> None:
        first_operand = self.pop_data()
        second_operand = self.pop_data()
        self._check_matching_operands(first_operand.datatype, second_operand.datatype)
        self._check_type(first_operand.datatype, [DataType.TYPE_INT, DataType.TYPE_STRING, DataType.TYPE_BOOL,
                         DataType.TYPE_FLOAT])
        
        source_var = self.get_var(dest_name, dest_frame)
        if first_operand.datatype == DataType.TYPE_INT:
            result = "true" if int(first_operand.value) > int(second_operand.value) else "false"

        if first_operand.datatype == DataType.TYPE_FLOAT:
            result = "true" if float(first_operand.value) > float(second_operand.value) else "false"

        if first_operand.datatype == DataType.TYPE_BOOL:
            result = "true" if convert_string_to_bool(first_operand.value) > convert_string_to_bool(second_operand.value) else "false"

        if first_operand.datatype == DataType.TYPE_STRING:
            result = "true" if first_operand.value > second_operand.value else "false"


        source_var.datatype = DataType.TYPE_BOOL
        source_var.value = result

    def eq(self, dest_name: str, dest_frame: str) -> None:
        first_operand = self.pop_data()
        second_operand = self.pop_data()

        # TODO neviem co tu spravit
        # if first_operand.datatype == DataType.TYPE_NIL:
            # if second_operand.datatype == DataType.TYPE_NIL

        self._check_matching_operands(first_operand.datatype, second_operand.datatype)
        
        result = "true"
        source_var = self.get_var(dest_name, dest_frame)
        if first_operand.datatype == DataType.TYPE_INT:
            result = "true" if int(first_operand.value) == int(second_operand.value) else "false"

        if first_operand.datatype == DataType.TYPE_FLOAT:
            result = "true" if float(first_operand.value) == float(second_operand.value) else "false"

        if first_operand.datatype == DataType.TYPE_BOOL:
            result = "true" if convert_string_to_bool(first_operand.value) == convert_string_to_bool(second_operand.value) else "false"

        if first_operand.datatype == DataType.TYPE_STRING:
            result = "true" if first_operand.value == second_operand.value else "false"

        if first_operand.datatype == DataType.TYPE_NIL:
            result = "true" if first_operand.value == second_operand.value else "false"

        source_var.datatype = DataType.TYPE_BOOL
        source_var.value = result

    def and_(self, dest_name: str, dest_frame: str) -> None: 
        first_operand = self.pop_data()
        second_operand = self.pop_data()

        self._check_type(first_operand.datatype, [DataType.TYPE_BOOL])
        self._check_matching_operands(first_operand.datatype, second_operand.datataype)

        source_var = self.get_var(dest_name, dest_frame)
        source_var.datatype = DataType.TYPE_BOOL
        source_var.value = convert_string_to_bool(first_operand.value) and convert_string_to_bool(second_operand.value)

    def or_(self, dest_name: str, dest_frame: str) -> None: 
        first_operand = self.pop_data()
        second_operand = self.pop_data()

        self._check_type(first_operand.datatype, [DataType.TYPE_BOOL])
        self._check_matching_operands(first_operand.datatype, second_operand.datataype)

        source_var = self.get_var(dest_name, dest_frame)
        source_var.datatype = DataType.TYPE_BOOL
        source_var.value = str(convert_string_to_bool(first_operand.value) or
                               convert_string_to_bool(second_operand.value))

    def not_(self, dest_name: str, dest_frame: str) -> None:
        operand = self.pop_data()
        self._check_type(operand.datatype, [DataType.TYPE_BOOL])
        source_var = self.get_var(dest_name, dest_frame)
        source_var.datatype = DataType.TYPE_BOOL
        source_var.value = str(not convert_string_to_bool(operand.value))
    
    
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

