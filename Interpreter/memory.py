from input_handler import ArgumentType

from error_codes import ErrorCodes
from debug import DEBUG_PRINT
from config import DEBUG
from instructions import DataType
from instructions import Variable

from typing import Callable


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
        self._call_stack = []


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

    def temp_frame_exists(self) -> bool:
        return self._temporary_frame is not None

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
    
    def check_var_set(self, name: str, frame: str) -> None:
        var = self.get_var(name, frame)
        if var.value is None:
            DEBUG_PRINT("Uninitialized variable")
            exit(ErrorCodes.CallStackEmpty)


    def set_var(self, name: str, frame: str, value: str, datatype: DataType) -> None:
        if value is None:
            DEBUG_PRINT("Uninitialized variable")
            exit(ErrorCodes.CallStackEmpty)

        var = self.get_var(name, frame)
        var.datatype = datatype
        var.value = value


    def _check_type(self, type_: DataType, allowed_types: list[DataType]) -> None:
        if type_ not in allowed_types:
            DEBUG_PRINT("Instruction wrong datatype")
            exit(ErrorCodes.OperandTypeBad)

    def _check_matching_operands(self, operand1_datatype: DataType, operand2_datatype: DataType) -> None:
        if operand1_datatype != operand2_datatype:
            DEBUG_PRINT("OPERAND datatypes not matching"+ str(operand1_datatype) + "/" + str(operand2_datatype))
            exit(ErrorCodes.OperandTypeBad)

    def _operation(self, function: Callable, dest_name, dest_frame, first_operand: Variable, second_operand: Variable, stack_only: bool = False):
        self._check_type(first_operand.datatype, [DataType.TYPE_INT, DataType.TYPE_FLOAT])
        self._check_matching_operands(first_operand.datatype, second_operand.datatype)

        if first_operand.datatype == DataType.TYPE_INT:
            result = str(function(int(first_operand.value), int(second_operand.value)))
        else:
            result = str(float.hex(function(float.fromhex(first_operand.value), float.fromhex(second_operand.value))))

        if stack_only:
            self.push_to_data_stack(result, first_operand.datatype)
            return

        self.set_var(dest_name, dest_frame, result, first_operand.datatype)

    def add(self, dest_name: str, dest_frame: str, stack_only: bool = False) -> None:
        first_operand = self.pop_from_data_stack()
        second_operand = self.pop_from_data_stack()

        self._operation(lambda x, y: x + y, dest_name, dest_frame, first_operand, second_operand, stack_only=stack_only)

    def sub(self, dest_name: str, dest_frame: str, stack_only: bool = False) -> None:
        second_operand = self.pop_from_data_stack()
        first_operand = self.pop_from_data_stack()

        self._operation(lambda x, y: x - y, dest_name, dest_frame, first_operand, second_operand, stack_only=stack_only)


    def mul(self, dest_name: str, dest_frame: str, stack_only: bool = False) -> None:
        first_operand = self.pop_from_data_stack()
        second_operand = self.pop_from_data_stack()

        self._operation(lambda x, y: x * y, dest_name, dest_frame, first_operand, second_operand, stack_only=stack_only)

    def idiv(self, dest_name: str, dest_frame: str, stack_only: bool = False) -> None:
        second_operand = self.pop_from_data_stack()
        first_operand = self.pop_from_data_stack()
        self._check_type(first_operand.datatype, [DataType.TYPE_INT])
        self._check_type(second_operand.datatype, [DataType.TYPE_INT])

        def check_function(x, y):
            try:
                return int(x) // int(y)
            except ZeroDivisionError:
                DEBUG_PRINT("IDIV by zero")
                exit(ErrorCodes.OperandValueBad)

        self._operation(check_function, dest_name, dest_frame, first_operand, second_operand, stack_only=stack_only)

    def div(self, dest_name: str, dest_frame: str, stack_only: bool = False) -> None:
        second_operand = self.pop_from_data_stack()
        first_operand = self.pop_from_data_stack()
        self._check_type(first_operand.datatype, [DataType.TYPE_FLOAT])
        self._check_type(second_operand.datatype, [DataType.TYPE_FLOAT])

        def check_function(x, y):
            try:
                return x / y
            except ZeroDivisionError:
                DEBUG_PRINT("IDIV by zero")
                exit(ErrorCodes.OperandValueBad)

        self._operation(check_function, dest_name, dest_frame, first_operand, second_operand, stack_only=stack_only)



    def _compare_operation(self, compare_function: Callable, dest_name: str, dest_frame: str, first_operand,
                           second_operand, stack_only: bool = False):
        result = "true" if compare_function(first_operand.value, second_operand.value) else "false"
        if stack_only:
            self.push_to_data_stack(result, DataType.TYPE_BOOL)
            return 

        self.set_var(dest_name, dest_frame, result, DataType.TYPE_BOOL)

    def lt(self, dest_name: str, dest_frame: str, stack_only: bool = False) -> None:
        second_operand = self.pop_from_data_stack()
        first_operand = self.pop_from_data_stack()
        self._check_matching_operands(first_operand.datatype, second_operand.datatype)
        self._check_type(first_operand.datatype, [DataType.TYPE_INT, DataType.TYPE_STRING, DataType.TYPE_BOOL,
                                                  DataType.TYPE_FLOAT])

        if first_operand.datatype == DataType.TYPE_INT:
            self._compare_operation(lambda x, y: True if int(x) < int(y) else False, dest_name, dest_frame,
                                    first_operand, second_operand, stack_only = stack_only)

        elif first_operand.datatype == DataType.TYPE_FLOAT:
            self._compare_operation(lambda x, y: True if float(x) < float(y) else False, dest_name, dest_frame,
                                    first_operand, second_operand, stack_only = stack_only)

        elif first_operand.datatype == DataType.TYPE_BOOL:
            self._compare_operation(lambda x, y: True if convert_string_to_bool(x) < convert_string_to_bool(y) else
                                    False, dest_name, dest_frame, first_operand, second_operand, stack_only=stack_only)

        elif first_operand.datatype == DataType.TYPE_STRING:
            self._compare_operation(lambda x, y: True if x < y else False, dest_name, dest_frame, first_operand,
                                    second_operand, stack_only=stack_only)


    def gt(self, dest_name: str, dest_frame: str, stack_only: bool = False) -> None:
        second_operand = self.pop_from_data_stack()
        first_operand = self.pop_from_data_stack()
        self._check_matching_operands(first_operand.datatype, second_operand.datatype)
        self._check_type(first_operand.datatype, [DataType.TYPE_INT, DataType.TYPE_STRING, DataType.TYPE_BOOL,
                                                  DataType.TYPE_FLOAT])

        if first_operand.datatype == DataType.TYPE_INT:
            self._compare_operation(lambda x, y: True if int(x) > int(y) else False, dest_name, dest_frame,
                                    first_operand, second_operand, stack_only = stack_only)

        elif first_operand.datatype == DataType.TYPE_FLOAT:

            self._compare_operation(lambda x, y: True if float(x) > float(y) else False, dest_name, dest_frame,
                                    first_operand, second_operand, stack_only = stack_only)

        elif first_operand.datatype == DataType.TYPE_BOOL:
            self._compare_operation(lambda x, y: True if convert_string_to_bool(x) > convert_string_to_bool(y) else
                                    False, dest_name, dest_frame, first_operand, second_operand, stack_only=stack_only)

        elif first_operand.datatype == DataType.TYPE_STRING:
            self._compare_operation(lambda x, y: True if x > y else False, dest_name, dest_frame, first_operand,
                                    second_operand, stack_only=stack_only)


    def eq(self, dest_name: str, dest_frame: str, stack_only: bool = False) -> None:
        first_operand = self.pop_from_data_stack()
        second_operand = self.pop_from_data_stack()

        # nil is a special case
        if first_operand.datatype == DataType.TYPE_NIL or second_operand.datatype == DataType.TYPE_NIL:
            if first_operand.datatype == second_operand.datatype:
                result = "true"
            else:
                result = "false"
            if stack_only:
                self.push_to_data_stack(result, DataType.TYPE_BOOL)
            else:
                self.set_var(dest_name, dest_frame, result, DataType.TYPE_BOOL)
            return 

        self._check_matching_operands(first_operand.datatype, second_operand.datatype)

        if first_operand.datatype == DataType.TYPE_INT:
            self._compare_operation(lambda x, y: int(first_operand.value) == int(second_operand.value),
                                    dest_name, dest_frame, first_operand, second_operand, stack_only=stack_only)

        elif first_operand.datatype == DataType.TYPE_FLOAT:
            self._compare_operation(lambda x, y: float(first_operand.value) == float(second_operand.value),
                                    dest_name, dest_frame, first_operand, second_operand, stack_only=stack_only)

        elif first_operand.datatype == DataType.TYPE_BOOL:
            self._compare_operation(lambda x, y: convert_string_to_bool(first_operand.value) ==
                                    convert_string_to_bool(second_operand.value),
                                    dest_name, dest_frame, first_operand, second_operand, stack_only=stack_only)

        elif first_operand.datatype in [DataType.TYPE_STRING, DataType.TYPE_NIL]:
            self._compare_operation(lambda x, y: first_operand.value == second_operand.value,
                                    dest_name, dest_frame, first_operand, second_operand, stack_only=stack_only)



    def and_(self, dest_name: str, dest_frame: str, stack_only: bool = False) -> None: 
        first_operand = self.pop_from_data_stack()
        second_operand = self.pop_from_data_stack()

        self._check_type(first_operand.datatype, [DataType.TYPE_BOOL])
        self._check_matching_operands(first_operand.datatype, second_operand.datatype)

        new_value = "true" if convert_string_to_bool(first_operand.value) and convert_string_to_bool(second_operand.value) else "false"
        if stack_only:
            self.push_to_data_stack(new_value, DataType.TYPE_BOOL)
            return

        self.set_var(dest_name, dest_frame, new_value, DataType.TYPE_BOOL)

    def or_(self, dest_name: str, dest_frame: str, stack_only: bool = False) -> None: 
        first_operand = self.pop_from_data_stack()
        second_operand = self.pop_from_data_stack()

        self._check_type(first_operand.datatype, [DataType.TYPE_BOOL])
        self._check_matching_operands(first_operand.datatype, second_operand.datatype)

        new_value = "true" if convert_string_to_bool(first_operand.value) or \
        convert_string_to_bool(second_operand.value) else "false"
        if stack_only:
            self.push_to_data_stack(new_value, DataType.TYPE_BOOL)
            return
        self.set_var(dest_name, dest_frame, new_value, DataType.TYPE_BOOL)

    def not_(self, dest_name: str, dest_frame: str, stack_only: bool = False) -> None:
        operand = self.pop_from_data_stack()
        self._check_type(operand.datatype, [DataType.TYPE_BOOL])
        new_value = "true" if not convert_string_to_bool(operand.value) else "false"
        if stack_only:
            self.push_to_data_stack(new_value, DataType.TYPE_BOOL)
            return 

        self.set_var(dest_name, dest_frame, new_value, DataType.TYPE_BOOL)

    def concat(self, dest_name: str, dest_frame: str) -> None:
        operand1 = self.pop_from_data_stack()
        operand2 = self.pop_from_data_stack()
        self._check_type(operand1.datatype, [DataType.TYPE_STRING])
        self._check_type(operand2.datatype, [DataType.TYPE_STRING])

        new_value = operand1.value + operand2.value
        self.set_var(dest_name, dest_frame, new_value, DataType.TYPE_STRING)


    def strlen(self, dest_name: str, dest_frame: str) -> None:
        operand = self.pop_from_data_stack()
        self._check_type(operand.datatype, [DataType.TYPE_STRING])
        new_value = len(operand.value)
        self.set_var(dest_name, dest_frame, new_value, DataType.TYPE_INT)


    # get char from string at index
    def getchar(self, dest_name: str, dest_frame: str) -> None:
        operand1 = self.pop_from_data_stack()
        operand2 = self.pop_from_data_stack()
        self._check_type(operand1.datatype, [DataType.TYPE_STRING])
        self._check_type(operand2.datatype, [DataType.TYPE_INT])
        if int(operand2.value) >= len(operand1.value) or int(operand2.value) < 0:
            DEBUG_PRINT("GETCHAR greater than length")
            exit(ErrorCodes.StringError)

        new_value = operand1.value[int(operand2.value)]
        self.set_var(dest_name, dest_frame, new_value, DataType.TYPE_STRING)

    # set char in string at index
    def setchar(self, dest_name: str, dest_frame: str) -> None:
        operand1 = self.pop_from_data_stack()
        operand2 = self.pop_from_data_stack()
        self._check_type(operand1.datatype, [DataType.TYPE_STRING])
        self._check_type(operand2.datatype, [DataType.TYPE_INT])

        var = self.get_var(dest_name, dest_frame)
        if int(operand2.value) >= len(var.value) or int(operand2.value) < 0:
            DEBUG_PRINT("GETCHAR greater than length")
            exit(ErrorCodes.StringError)

        index = int(operand2.value)
        new_char = operand1.value[0]
        new_string = var.value[:index] + new_char + var.value[index + 1:]
        self.set_var(dest_name, dest_frame, new_string, DataType.TYPE_STRING)

    # testing function
    def get_frame_stack(self) -> list[Frame]:
        return self._frame_stack

    def get_global_frame(self) -> Frame:
        return self._global_frame

    # ///--------- FUNCTIONS WITH DATA STACK -------\\\\\\ 

    # push data on top of the data stack
    def push_to_data_stack(self, value: str, datatype: DataType) -> None:
        # "stack_var" is default name for stack variables - they can be anonymous
        new_var = Variable("stack_var")
        new_var.value = value
        new_var.datatype = datatype
        self._data_stack.append(new_var)

    # pop data from the top of the data stack

    def pop_from_data_stack(self) -> str:
        if len(self._data_stack) == 0:
            DEBUG_PRINT("Data stack is empty")
            exit(ErrorCodes.CallStackEmpty)

        return self._data_stack.pop(-1)

    # clear the data stack 
    def clear_data_stack(self) -> int:
        del self._data_stack
        self._data_stack = []

    # push current index to call stack
    # when running CALL instruction
    def push_to_call_stack(self, index: int) -> None:
        self._call_stack.append(index)

    # pop index from call stack
    # if it's empty exit with error
    def pop_from_call_stack(self) -> int:
        if not len(self._call_stack):
            DEBUG_PRINT("Call stack is empty")
            exit(ErrorCodes.CallStackEmpty)
        return self._call_stack.pop(-1)
    
