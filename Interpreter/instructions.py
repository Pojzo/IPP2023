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
    type_int = 1
    type_string = 2
    type_bool = 3
    type_nil = 4
    type_float = 5

    @staticmethod
    def convert_to_enum(datatype: str) -> "DataType":
        if datatype == "int":
            return DataType.type_int
        elif datatype == "string":
            return DataType.type_string
        elif datatype == "bool":
            return DataType.type_bool
        elif datatype == "nil":
            return DataType.type_nil
        elif datatype == "float":
            return DataType.type_float



class Instruction(abc.ABC):
    def __init__(self, opcode: str, args: list[Argument]):
        self.opcode = opcode
        self._args = args
        if not self.check_argument_types():
            DEBUG_PRINT("Check argument types failed")
            exit(ErrorCodes.InputNotWellFormed)


    # i don't know if this is necessary but whatever
    def check_argument_types(self):
        expected_types = instructions_dic[self.opcode]
        our_types = [arg.type_ for arg in self._args]
        return True
        # return all([a == b for a, b in zip(expected_types, our_types)])

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
        return {'int':       type_int,
                'string':    type_string,
                'bool': type_bool,
                'nil':  type_nil}[str_datatype]

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
            memory.set_var(dest_name, dest_frame, source_value, source_datatype)
             

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

    def execute(self, memory):
        pass

# ADD ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class ADD(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def push_var(self, memory, operand_arg: str) -> None:
        operand_name = self.get_name_from_arg_value(operand_arg.value)
        operand_frame = self.get_frame_from_arg_value(operand_arg.value)
        operand_var = memory.get_var(operand_name, operand_frame)

        memory.push_data(operand_var.value, operand_var.datatype)


    def execute(self, memory):
        source_arg, operand1_arg, operand2_arg = self._args
        
        source_name = self.get_name_from_arg_value(source_arg.value)
        source_frame = self.get_frame_from_arg_value(source_arg.value)
        
        if operand1_arg.type_ == ArgumentType.VAR:
            self.push_var(memory, operand1_arg)
        else:
            memory.push_data(operand1_arg.value, DataType.convert_to_enum(operand1_arg.datatype))

        if operand2_arg.type_ == ArgumentType.VAR:
            self.push_var(memory, operand2_arg)
        else:
            memory.push_data(operand2_arg.value, DataType.convert_to_enum(operand2_arg.datatype))

        memory.add(source_name, source_frame)


 # SUB ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class SUB(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        pass

# MUL ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class MUL(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        pass

# IDIV ⟨var⟩ ⟨symb1⟩ ⟨symb2⟩
class IDIV(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(self.__class__.__name__, args)

    def execute(self, memory):
        pass
