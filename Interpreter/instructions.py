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
        self.__args = args

    @abc.abstractmethod
    def execute(self, memory) -> None:
        """ Each instruction must implement
            its own execute function
            """
        pass
    
    # extract the frame from variable string
    def get_frame_from_var(self, var: str) -> str:
        return var[:2]

    def convert_strings_data_type_to_enum(self, str_datatype) -> DataType:
        return {'int':       type_int,
                'string':    type_string,
                'bool': type_bool,
                'nil':  type_nil}[str_datatype]

    def __repr__(self):
        return f"{str(type(self))}, {self.__args}"

# DEFVAR ⟨var⟩
class DEFVAR(Instruction):
    def __init__(self, args: list[Argument]):
        super().__init__(type_, args)

    def execute(self, memory):
        var_arg = self.__args[0]
        frame = self.get_frame_from_var(var_arg.value)

        if memory.var_already_defined():
            DEBUG_PRINT(f"Variable {var_args.value} in frame {frame} already defined")
            exit(ErrorCodes.VariableRedefinition)

        memory.define_var(self.__args[0].type_, self.__args[0].value)
        

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
