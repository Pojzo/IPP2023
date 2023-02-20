from input_handler import InputHandler
from input_handler import Argument
from memory import Memory
import instructions as InstructionsClass

inpt = InputHandler()
inpt.parse_arguments()
inpt.parse_input()
inpt.convert_source()
inpt.verify_structure()


# the interpreter gets list of lines from input handler
class Interpreter:
    def __init__(self, instructions_raw: list[str, list[Argument]]):
        self.__instructions = []
        self.__memory = Memory()
        self.create_instructions(instructions_raw)

    # created __instructions list of instruction objects
    # based on opcode string and arguments
    def create_instructions(self,
                            instructions_raw: list[str, list[Argument]]) -> None:

        for opcode, args in instructions_raw:
            # dynamically create instruction object based on opcode string
            instruction_obj = getattr(InstructionsClass, opcode)(opcode, args)
            self.__instructions.append(instruction_obj)

    def print_instructions(self):
        for instruction in self.__instructions:
            print(instruction)


interpreter = Interpreter(inpt.get_instructions())
interpreter.print_instructions()
