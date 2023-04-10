from input_handler import ArgumentType
from input_handler import Argument
from debug import DEBUG_PRINT

import abc

class DataType:
     type_int = 1
     type_string = 2
     type_bool = 3
     type_nil = 4


class Instruction(abc.ABC):
    def __init__(self, args: list[Argument]):
        self._args = args

    @abc.abstractmethod
    def execute(self, memory) -> None:
        """ Each instruction must implement
            its own execute function
            """
        pass
    
    # extract the frame from variable string
    def get_frame_from_var(self, var: str) -> str:
        return var.split('@')[0]

    def get_name_from_value(self, var: str) -> str:
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
        super().__init__(args)

    def execute(self, memory):
        frame = self.get_frame_from_var(self._args[0].value)
        name = self.get_name_from_value(self._args[0].value)
        memory.define_var(name, frame)
       
#////---------- INSTRUCTIONS RELATED TO FRAMES ----------//// 

class CREATEFRAME(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(args)

    def execute(self, memory):
        memory.create_frame()

class PUSHFRAME(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(args)

    def execute(self, memory):
        memory.push_frame()

class POPFRAME(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(args)

    def execute(self, memory):
        memory.pop_frame()

# MOVE ⟨var⟩ ⟨symb⟩
class MOVE(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(args)

    def execute(self):
        pass

# READ ⟨var⟩ ⟨type⟩
class READ(Instruction):
    def __init__(self, type_, args: list[Argument]):
        super().__init__(type_, args)

    def execute(self):
        pass


# WRITE ⟨symb⟩
class WRITE(Instruction):
    def __init__(self, type_, args: list[Argument]):
        super().__init__(type_, args)

    def execute(self):
        pass
