from input_handler import InputHandler
from input_handler import instructions_dic
from input_handler import ArgumentType
from input_handler import Argument
from memory import Memory

from config import DEBUG


inpt = InputHandler()
inpt.parse_arguments()
inpt.parse_input()
inpt.convert_source()
inpt.verify_structure()


# the interpreter gets list of lines from input handler
class Interpreter:
    def __init__(self, instructions: list[str, list[Argument]]):
        self.__instructions = instructions
        self.__memory = Memory()
        # self.__opcode_func = {

    def print_instructions(self):
        for instruction in self.__instructions:
            print("opcode:", instruction[0], "arguments:", instruction[1])


class Instruction:
    def __init__(self, type_, args: list[Argument]):
        self.__type = type_
        self.__args = args


    def var_exists(self, arg: Argument):
        if arg.get_type() == ArgumentType.VAR:
            if not self.__memory.var_exists(arg.get_value()):
                raise Exception("Variable does not exist")

# MOVE ⟨var⟩ ⟨symb⟩
# Přiřazení hodnoty do proměnné
# Zkopíruje hodnotu ⟨symb⟩ do ⟨var⟩. Např. MOVE LF@par GF@var provede zkopírování hodnoty
# proměnné var v globálním rámci do proměnné par v lokálním rámci.
class MOVE(Instruction):
    def __init__(self, type_, args: list[Argument]):
        super().__init__(type_, args)

    def execute(self):
        var_exists(self.__args[0])


interpreter = Interpreter(inpt.get_instructions())
interpreter.print_instructions()
