from input_handler import ArgumentType
from input_handler import Argument
from input_handler import instructions_dic
from debug import DEBUG_PRINT
from error_codes import ErrorCodes
from typing import Callable

import re


import abc

class Variable:
    def __init__(self, name_: str):
        self.name = name_
        self.value = None
        self.datatype: DataType = None
 
class DataType:
    TYPE_INT = 1
    TYPE_STRING = 2
    TYPE_BOOL = 3
    TYPE_NIL = 4
    TYPE_FLOAT = 5

    @staticmethod
    def convert_to_enum(datatype: str) -> "DataType":
        if datatype == "int":
            return DataType.TYPE_INT
        elif datatype == "string":
            return DataType.TYPE_STRING
        elif datatype == "bool":
            return DataType.TYPE_BOOL
        elif datatype == "nil":
            return DataType.TYPE_NIL
        elif datatype == "float":
            return DataType.TYPE_FLOAT

    @staticmethod
    def convert_to_string(datatype: "DataType") -> str:
        if datatype == DataType.TYPE_INT:
            return "int"
        elif datatype == DataType.TYPE_STRING:
            return "string"
        elif datatype == DataType.TYPE_BOOL:
            return "bool"
        elif datatype == DataType.TYPE_NIL:
            return "nil"
        elif datatype == DataType.TYPE_FLOAT:
            return "float"


class Instruction(abc.ABC):
    instrucion_index_callback: Callable[[], int]
    input_stream: "Input"
    def __init__(self, opcode: str, args: list[Argument]):
        self.opcode = opcode
        self._args = args
        self.check_argument_types()

    # i don't know if this is necessary but whatever
    def check_argument_types(self):
        for arg, expected_type in zip(self._args, instructions_dic[self.opcode]):
            if arg.datatype == "int":
                try:
                    int(arg.value)
                except Exception as e:
                    DEBUG_PRINT("Bad int on input")

                    exit(ErrorCodes.InputStructureBad)

            if arg.datatype == "float":
                try:
                    float.fromhex(arg.value)
                except Exception as e:
                    DEBUG_PRINT("Bad float on input")
                    exit(ErrorCodes.InputStructureBad)

            if arg.datatype == "bool":
                if not arg.value.lower() in ["true", "false"]:
                    DEBUG_PRINT("Bad bool on input")
                    exit(ErrorCodes.InputStructureBad)
            
            if expected_type == ArgumentType.SYMB:
                if arg.type_ in [ArgumentType.SYMB, ArgumentType.VAR]:
                    continue

            if not arg.type_ == expected_type:
                DEBUG_PRINT("Not good type ")
                exit(ErrorCodes.InputStructureBad)

    @abc.abstractmethod
    def execute(self, memory) -> None:
        """ Each instruction must implement
            its own execute function
            """
        pass

    def get_frame_from_arg_value(self, var: str) -> str:
        return var.split('@')[0]

    def get_name_from_arg_value(self, var: str) -> str:
        return var.split('@')[1]
    
    def push_var_to_stack(self, arg, memory) -> None:
        if arg.type_ == ArgumentType.VAR:
            name = self.get_name_from_arg_value(arg.value)
            frame = self.get_frame_from_arg_value(arg.value)
            var = memory.get_var(name, frame)
            memory.push_to_data_stack(var.value, var.datatype)
        else:
            memory.push_to_data_stack(arg.value, DataType.convert_to_enum(arg.datatype))

    def get_var_from_arg(self, arg: Argument) -> tuple[str, str]:
        name = self.get_name_from_arg_value(arg.value)
        frame = self.get_frame_from_arg_value(arg.value)
        return name, frame

    def __repr__(self):
        return f"{str(type(self))}, {self._args}"

# DEFVAR ⟨var⟩
class DEFVAR(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        frame = self.get_frame_from_arg_value(self._args[0].value)
        name = self.get_name_from_arg_value(self._args[0].value)
        memory.define_var(name, frame)

#////---------- INSTRUCTIONS RELATED TO FRAMES ----------//// 

class CREATEFRAME(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        memory.create_frame()

class PUSHFRAME(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        memory.push_frame()

class POPFRAME(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        memory.pop_frame()

#////---------- INSTRUCTIONS RELATED TO THE DATA STACK ----------////
class PUSHS(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        arg = self._args[0]
        value = arg.value

        # if it's a variable
        if arg.type_ == ArgumentType.VAR:
            name = get_name_from_arg_value(arg.value)
            frame = self.get_frame_from_arg_value(arg.value)
            var = memory.get_var(name, frame)
            memory.push_to_data_stack(var.value, var.datatype)

        # it's a constant
        else:
            data_type = DataType.convert_to_enum(arg.datatype)
            memory.push_to_data_stack(value, data_type)


# POP ⟨var⟩
class POPS(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        arg = self._args[0]
        name = self.get_name_from_arg_value(arg.value)
        frame = self.get_frame_from_arg_value(arg.value)
        popped = memory.pop_from_data_stack()
        memory.set_var(name, frame, popped.value, popped.datatype)


# MOVE ⟨var⟩ ⟨symb⟩
class MOVE(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        dest_arg, source_arg  = self._args
        dest_name, dest_frame = self.get_var_from_arg(dest_arg)

        if source_arg.type_ == ArgumentType.VAR:
            source_name, source_frame = self.get_var_from_arg(source_arg)
            var = memory.get_var(source_name, source_frame)
            memory.set_var(dest_name, dest_frame, var.value, var.datatype)

        else:
            source_datatype = source_arg.datatype
            source_value = source_arg.value
            memory.set_var(dest_name, dest_frame, source_value, DataType.convert_to_enum(source_datatype))


# READ ⟨var⟩ ⟨type⟩
class READ(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        var_arg = self._args[0]
        type_arg = self._args[1]
        if type_arg.value not in ["string", "int", "bool", "float"]:
            DEBUG_PRINT("Bad type on input")
            exit(ErrorCodes.InputStructureBad)
        
        var_name = self.get_name_from_arg_value(var_arg.value)
        var_frame = self.get_frame_from_arg_value(var_arg.value)
        var = memory.get_var(var_name, var_frame)

        
        value = Instruction.input_stream.readline().strip('\n')
        if len(value) == 0:
            memory.set_var(var_name, var_frame, value, DataType.TYPE_NIL)
            return
            # special case nil@nil
        

        memory.set_var(var_name, var_frame, value, DataType.convert_to_enum(type_arg.value))


# WRITE ⟨symb⟩
class WRITE(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    # find any escaped sequences and convert them to ascii
    def _convert_to_ascii(self, string: str) -> str:
        pattern = r'\\[0-9]{3}'
        new_string = string
        new_string = re.sub(pattern, lambda m: chr(int(m.group(0)[1:])), new_string)
        new_string = new_string.replace('\\', '')

        return new_string


    def _write_const(self, value: str, datatype: DataType):
        # print(f"Printing this value: _{value}_")
        if datatype == DataType.TYPE_NIL:
            print(end='')

        elif datatype == DataType.TYPE_INT:
            if '.' in value:
                print(int(float(value)), end='')

            else:
                print(int(value), end='')
        elif datatype == DataType.TYPE_FLOAT:
            print(float.hex(float.fromhex(value)), end='')
        else:
            print_value = self._convert_to_ascii(value)
            if len(print_value):
                print(print_value, end='')

    def execute(self, memory):
        arg = self._args[0]
        if arg.type_ == ArgumentType.VAR:
            name = self.get_name_from_arg_value(arg.value)
            frame = self.get_frame_from_arg_value(arg.value)
            var = memory.get_var(name, frame)
            self._write_const(var.value, var.datatype)
        else:
            value = arg.value
            datatype = DataType.convert_to_enum(arg.datatype)
            self._write_const(value, datatype)


class ArithmeticInstruction(Instruction):
    def __init__(self, opcode: str, args: list[Argument]):
        super().__init__(opcode, args)

    def execute(self, memory, function_name):
        source_arg, operand1_arg, operand2_arg = self._args
        self.push_var_to_stack(operand1_arg, memory)
        self.push_var_to_stack(operand2_arg, memory)

        # find the method name dynamically
        source_name = self.get_name_from_arg_value(source_arg.value)
        source_frame = self.get_frame_from_arg_value(source_arg.value)
        callback = getattr(memory, function_name)
        callback(source_name, source_frame)


# ADD ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class ADD(ArithmeticInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "add")


 # SUB ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class SUB(ArithmeticInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "sub")

# MUL ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class MUL(ArithmeticInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "mul")

# IDIV ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class IDIV(ArithmeticInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "idiv")

# LT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class LT(ArithmeticInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "lt")

# GT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class GT(ArithmeticInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "gt")


# EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class EQ(ArithmeticInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "eq")


# AND ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class AND(ArithmeticInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "and_")

# OR ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class OR(ArithmeticInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "or_")

# NOT ⟨var⟩ ⟨symb1⟩
class NOT(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        source_arg, operand1_arg= self._args
        source_name = self.get_name_from_arg_value(source_arg.value)
        source_frame = self.get_frame_from_arg_value(source_arg.value)

        self.push_var_to_stack(operand1_arg, memory)
        memory.not_(source_name, source_frame)


class ArithmeticStackInstruction(Instruction):
    def __init__(self, opcode: str, args: list[Argument]):
        super().__init__(opcode, args)

    def execute(self, memory, function_name):
        callback = getattr(memory, function_name)
        # we don't need to pass any variable to store the result to
        callback("", "", stack_only=True)

class ADDS(ArithmeticStackInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "add")

class SUBS(ArithmeticStackInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "sub")

class MULS(ArithmeticStackInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "mul")

class IDIVS(ArithmeticStackInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "idiv")

class LTS(ArithmeticStackInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "lt")

# GT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class GTS(ArithmeticStackInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "gt")


# EQ ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class EQS(ArithmeticStackInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "eq")


class ANDS(ArithmeticStackInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "and_")

class ORS(ArithmeticStackInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "or_")

class NOTS(ArithmeticStackInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "not_")



       
# TYPE ⟨var⟩ ⟨symb⟩
class TYPE(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        var_arg = self._args[0]
        symb_arg = self._args[1]

        var_name = self.get_name_from_arg_value(var_arg.value)
        var_frame = self.get_frame_from_arg_value(var_arg.value)
        var = memory.get_var(var_name, var_frame)

        if symb_arg.type_ == ArgumentType.VAR:
            symb_name = self.get_name_from_arg_value(var_arg.value)
            symb_frame = self.get_frame_from_arg_value(var_arg.value)
            symb_var = memory.get_var(symb_name, symb_frame)
            if symb_var.datatype == None:
                var.value = ""
            else:
                memory.set_var(DataType.convert_to_string(symb_var.datatype, DataType.TYPE_STRING))

        else:
            var.value = symb_arg.datatype

class ConvertInstruction(Instruction):
    def __init__(self, opcode: str, args: list[Argument]):
        super().__init__(opcode, args)

    def _convert_to_chr(self, value: str) -> chr:
        try: 
            return chr(int(value))
        except:
            DEBUG_PRINT("Failed to convert int to chr")
            exit(ErrorCodes.StringError)

    def _convert_string_to_int(self, value: str) -> chr:
        try:
            return str(ord(value))
        except:
            DEBUG_PRINT("Failed to convert chr to int")
            exit(ErrorCodes.StringError)

    def _convert_float_to_int(self, value: str) -> int:
        try:
            return int(float.fromhex(value))
        except:
            DEBUG_PRINT("Failed to convert float to int")
            exit(ErrorCodes.OperandTypeBad)

    def _convert_int_to_float(self, value: str) -> int:
        try:
            return float.hex(int(value))
        except:
            DEBUG_PRINT("Failed to convert int to float")
            exit(ErrorCodes.OperandTypeBad)



# INT2CHAR ⟨var⟩ ⟨symb⟩
class INT2CHAR(ConvertInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        dest_arg = self._args[0]
        source_arg = self._args[1]

        if source_arg.type_ == ArgumentType.VAR:
            source_name, source_frame = self.get_var_from_arg(source_arg)
            source_var = memory.get_var(source_name, source_frame)
            if source_var.datatype != DataType.TYPE_INT:
                DEBUG_PRINT("INT2CHAR bad type")
                exit(ErrorCodes.OperandTypeBad)
            new_value = self._convert_to_chr(source_var.value)
        else:
            new_value = self._convert_to_chr(source_arg.value)

        dest_name, dest_frame = self.get_var_from_arg(dest_arg)

        memory.set_var(dest_name, dest_frame, new_value, DataType.TYPE_STRING)

# INT2FLOAT ⟨var⟩ ⟨symb⟩
class INT2FLOAT(ConvertInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        dest_arg = self._args[0]
        source_arg = self._args[1]

        if source_arg.type_ == ArgumentType.VAR:
            source_name, source_frame = self.get_var_from_arg(source_arg)
            source_var = memory.get_var(source_name, source_frame)
            if source_var.datatype != DataType.TYPE_INT:
                DEBUG_PRINT("INT2CHAR bad type")
                exit(ErrorCodes.OperandTypeBad)
            new_value = self._convert_int_to_float(source_var.value)
        else:
            new_value = self._convert_int_to_float(source_arg.value)

        dest_name, dest_frame = self.get_var_from_arg(dest_arg)

        memory.set_var(dest_name, dest_frame, new_value, DataType.TYPE_FLOAT)


# INT2FLOAT ⟨var⟩ ⟨symb⟩
class FLOAT2INT(ConvertInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        dest_arg = self._args[0]
        source_arg = self._args[1]

        if source_arg.type_ == ArgumentType.VAR:
            source_name, source_frame = self.get_var_from_arg(source_arg)
            source_var = memory.get_var(source_name, source_frame)
            if source_var.datatype != DataType.TYPE_INT:
                DEBUG_PRINT("INT2CHAR bad type")
                exit(ErrorCodes.OperandTypeBad)

            new_value = self._convert_float_to_int(source_var.value)
        else:
            new_value = self._convert_float_to_int(source_arg.value)

        dest_name, dest_frame = self.get_var_from_arg(dest_arg)

        memory.set_var(dest_name, dest_frame, str(new_value), DataType.TYPE_INT)



# INT2CHARS
class INT2CHARS(ConvertInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        var = memory.pop_from_data_stack()
        if var.datatype != DataType.TYPE_INT:
            DEBUG_PRINT("INT2CHARS bad type")
            exit(ErrorCodes.OperandTypeBad)

        value = self._convert_to_chr(var.value)
        memory.push_to_data_stack(value, DataType.TYPE_STRING)

# STR2INT ⟨var⟩ ⟨symb⟩
class STRI2INT(ConvertInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        dest_arg, source_arg, index_arg = self._args
        dest_name, dest_frame = self.get_var_from_arg(dest_arg)

        if source_arg.type_ == ArgumentType.VAR:
            source_name, source_frame = self.get_var_from_arg(source_arg)
            source_var = memory.get_var(source_name, source_frame)
            if source_var.datatype != DataType.TYPE_STRING:
                DEBUG_PRINT("STRI2INT bad source type")
                exit(ErrorCodes.OperandTypeBad)

            source_value = source_var.value
        else:
            source_value = source_arg.value

        if index_arg.type_ == ArgumentType.VAR:
            index_name, index_frame = self.get_var_from_arg(index_arg)
            index_var = memory.get_var(index_name, index_frame)
            if index_var.datatype != DataType.TYPE_INT:
                DEBUG_PRINT("STRI2INT bad index type")
                exit(ErrorCodes.OperandTypeBad)

            index_value = int(index_var.value)
        else:
            index_value = int(index_arg.value)

        if index_value < 0 or index_value >= len(source_value):
            DEBUG_PRINT("Out of bounds index")
            exit(ErrorCodes.StringError)

        converted = self.convert_string_to_int(source_value[index_value])
        memory.set_var(dest_name, dest_frame, converted, DataType.TYPE_INT)


# STRI2INTS
class STRI2INTS(ConvertInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        index_var = memory.pop_from_data_stack()
        source_var = memory.pop_from_data_stack()

        if source_var.datatype != DataType.TYPE_STRING:
            DEBUG_PRINT("STR2INTS bad source type")
            exit(ErrorCodes.OperandTypeBad)

        if index_var.datatype != DataType.TYPE_INT:
            DEBUG_PRINT("STR2INTS bad index type")
            exit(ErrorCodes.OperandTypeBad)

        if int(index_var.value) <0 or (int(index_var.value) >= len(source_var.value)):
            DEBUG_PRINT("Out of bounds index")
            exit(ErrorCodes.StringError)

        converted = self.convert_string_to_int(source_var.value[int(index_var.value)])
        memory.push_to_data_stack(converted, DataType.TYPE_INT)


# CONCAT ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class CONCAT(ArithmeticInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "concat")

# STRLEN ⟨var⟩ ⟨symb⟩
class STRLEN(ArithmeticInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "strlen")

# GETCHAR ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class GETCHAR(ArithmeticInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "getchar")

# SETCHAR ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class SETCHAR(ArithmeticInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        super().execute(memory, "setchar")

class DPRINT(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        pass

class BREAK(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        pass

# JUMP
class JUMP(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        arg = self._args[0]
        return arg.value

temp_var_index = 0

class JumpInstruction(Instruction):
    def __init__(self, opcode: str, args: list[Argument]):
        super().__init__(opcode, args)

    def _push_var(self, memory):
        global temp_var_index
        label_arg, first_arg, second_arg = self._args

        self.push_var_to_stack(first_arg, memory)
        self.push_var_to_stack(second_arg, memory)

        # put the temporary memory in Global frame
        memory.define_var("<temp_result>" + str(temp_var_index), "GF")


# JUMPIFEQ
class JUMPIFEQ(JumpInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        global temp_var_index
        label_arg = self._args[0]
        self._push_var(memory)     

        memory.eq("<temp_result>" + str(temp_var_index), "GF")
        result = memory.get_var("<temp_result>" + str(temp_var_index), "GF")
        temp_var_index += 1
        if result.value == "true":
            return label_arg.value


# JUMPIFEQ
class JUMPIFNEQ(JumpInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        label_arg = self._args[0]
        global temp_var_index
        self._push_var(memory)
        memory.eq("<temp_result>" + str(temp_var_index), "GF")

        result = memory.get_var("<temp_result>" + str(temp_var_index), "GF")

        temp_var_index += 1
        if result.value == "false":
            return label_arg.value

class JUMPIFEQS(JumpInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        label_arg = self._args[0]
        global temp_var_index

        memory.define_var("<temp_result>" + str(temp_var_index), "GF")
        memory.eq("<temp_result>" + str(temp_var_index), "GF")
        result = memory.get_var("<temp_result>" + str(temp_var_index), "GF")
        temp_var_index += 1
        if result.value == "true":
            return label_arg.value

class JUMPIFNEQS(JumpInstruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        label_arg = self._args[0]
        global temp_var_index
        memory.define_var("<temp_result>" + str(temp_var_index), "GF")
        memory.eq("<temp_result>" + str(temp_var_index), "GF")
        result = memory.get_var("<temp_result>" + str(temp_var_index), "GF")
        temp_var_index += 1
        if result.value == "false":
            return label_arg.value



# LABEL   
class LABEL(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        pass

# CALL <label>
class CALL(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        label_arg = self._args[0]
        cur_index = Instruction.instruction_index_callback()
        memory.push_to_call_stack(cur_index + 1)
        return label_arg.value

# RETURN
class RETURN(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        index = memory.pop_from_call_stack()
        return index

# EXIT <symb>
class EXIT(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        arg = self._args[0]
        if arg.type_ == ArgumentType.VAR:
            name = self.get_name_from_arg_value(arg.value)
            frame = self.get_frame_from_arg_value(arg.value)
            var = memory.get_var(name, frame)
            if var.datatype != DataType.TYPE_INT:
                # TODO nie som si isty
                DEBUG_PRINT("Exit bad operand 1")
                exit(ErrorCodes.OperandValueBad)

            try:
                x = int(var.value)
            except:
                DEBUG_PRINT("Exit bad operand 2")
                exit(ErrorCodes.OperandValueBad)

            if x >= 0 and x <= 49:
                exit(x)
            else:
                DEBUG_PRINT("Exit bad operand 3")
                exit(ErrorCodes.OperandValueBad)

        if arg.datatype != "int":
            DEBUG_PRINT("Exit bad operand 4")
            exit(ErrorCodes.OperandValueBad)

        try:
            x = int(arg.value)
        except Exception as e:
            DEBUG_PRINT("Exit bad operand 5")
            exit(ErrorCodes.OperandValueBad)

        if x >= 0 and x <= 49:
            exit(x)
        else:
            DEBUG_PRINT("Exit bad operand 6")
            exit(ErrorCodes.OperandValueBad)

class CLEARS(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        memory.clear_data_stack()
