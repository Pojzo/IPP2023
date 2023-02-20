from input_handler import ArgumentType
from input_handler import Argument


class Instruction:
    def __init__(self, opcode: str, args: list[Argument]):
        self.__opcode = opcode
        self.__args = args

    def var_exists(self, arg: Argument):
        if arg.get_type() == ArgumentType.VAR:
            if not self.__memory.var_exists(arg.get_value()):
                raise Exception("Variable does not exist")

    def __repr__(self):
        return f"{self.__opcode} {self.__args}"


# MOVE ⟨var⟩ ⟨symb⟩
class MOVE(Instruction):
    def __init__(self, type_, args: list[Argument]):
        super().__init__(type_, args)

    def execute(self):
        pass


# DEFVAR ⟨var⟩
class DEFVAR(Instruction):
    def __init__(self, type_, args: list[Argument]):
        super().__init__(type_, args)

    def execute(self):
        pass


# READ ⟨var⟩ ⟨type⟩
class READ(Instruction):
    def __init__(self, type_, args: list[Argument]):
        super().__init__(type_, args)

    def execute(self):
        pass


class WRITE(Instruction):
    def __init__(self, type_, args: list[Argument]):
        super().__init__(type_, args)

    def execute(self):
        pass
