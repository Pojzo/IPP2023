from input_handler import ArgumentType
from input_handler import Argument
from input_handler import instructions_dic
from debug import DEBUG_PRINT
from error_codes import ErrorCodes


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


class Instruction(abc.ABC):
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
                    int(arg.value)
                except Exception as e:
                    DEBUG_PRINT("Bad float on input")
                    exit(ErrorCodes.InputStructureBad)

            if arg.datatype == "bool":
                if not arg.value in ["true", "false"]:
                    DEBUG_PRINT("Bad bool on input")
                    exit(ErrorCodes.InputStructureBad)
            
            if arg.type_ == ArgumentType.VAR and expected_type == ArgumentType.SYMB:
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

    def convert_strings_data_type_to_enum(self, str_datatype) -> DataType:
        return {'int':       TYPE_INT,
                'string':    TYPE_STRING,
                'bool': TYPE_BOOL,
                'nil':  TYPE_NIL,
                'float': TYPE_FLOAT}[str_datatype]

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
            memory.push_data(var.value, var.datatype)

        # it's a constant
        else:
            data_type = DataType.convert_to_enum(arg.datatype)
            memory.push_data(value, data_type)


# POP ⟨var⟩
class POPS(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        arg = self._args[0]
        name = get_name_from_arg_value(arg.value)
        frame = self.get_frame_from_arg_value(arg.value)
        popped = memory.pop_data()
        memory.set_var(name, frame, popped.value, popped.datatype)



# MOVE ⟨var⟩ ⟨symb⟩
class MOVE(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        dest_arg, source_arg  = self._args
        dest_name = self.get_name_from_arg_value(dest_arg.value)
        dest_frame = self.get_frame_from_arg_value(dest_arg.value)

        if source_arg.type_ == ArgumentType.VAR:
            source_name = self.get_name_from_arg_value(dest_arg.value)
            source_frame = self.get_frame_from_arg_value(dest_arg.value)
            memory.move_var(source_name, source_frame, dest_name, dest_frame)

        else:
            source_datatype = source_arg.datatype
            source_value = source_arg.value
            memory.set_var(dest_name, dest_frame, source_value, DataType.convert_to_enum(source_datatype))


# READ ⟨var⟩ ⟨type⟩
class READ(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        pass


# WRITE ⟨symb⟩
class WRITE(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def _write_var(self, var: Variable) -> None:
        value = var.value
        if var.datatype == DataType.TYPE_NIL:
            print(end='')

        elif var.datatype == DataType.TYPE_INT:
            if '.' in value:
                print(int(float(value)), end='')

            else:
                print(int(value), end='')
        elif var.datatype == DataType.TYPE_FLOAT:
            print(float(value), end='')
        else:
            print(value, end='')


    def execute(self, memory):
        arg = self._args[0]
        if arg.type_ == ArgumentType.VAR:
            name = self.get_name_from_arg_value(arg.value)
            frame = self.get_frame_from_arg_value(arg.value)
            var = memory.get_var(name, frame)
            self._write_var(var)


class ArithmeticInstruction(Instruction):
    def __init__(self, opcode: str, args: list[Argument]):
        super().__init__(opcode, args)

    # push variable onto the data stack
    # so it can be used by an operation in the memory
    def _push_var(self, memory, operand_arg: str) -> None:
        operand_name = self.get_name_from_arg_value(operand_arg.value)
        operand_frame = self.get_frame_from_arg_value(operand_arg.value)
        operand_var = memory.get_var(operand_name, operand_frame)

        memory.push_data(operand_var.value, operand_var.datatype)

    def execute(self, memory, function_name):
        source_arg, operand1_arg, operand2_arg = self._args

        source_name = self.get_name_from_arg_value(source_arg.value)
        source_frame = self.get_frame_from_arg_value(source_arg.value)

        # check if we're dealing with a variable 
        # or a symbol
        if operand2_arg.type_ == ArgumentType.VAR:
            self._push_var(memory, operand2_arg)
        else:
            memory.push_data(operand2_arg.value, DataType.convert_to_enum(operand2_arg.datatype))

        if operand1_arg.type_ == ArgumentType.VAR:
            self._push_var(memory, operand1_arg)
        else:
            memory.push_data(operand1_arg.value, DataType.convert_to_enum(operand1_arg.datatype))


        # find the method name dynamically
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
