from input_handler import InputHandler
from input_handler import Argument
from memory import Memory
import instructions as InstructionsClass


# the interpreter gets list of lines from input handler
class Interpreter:
    def __init__(self, instructions_raw: list[str, list[Argument]]):
        self._instructions = []
        self._create_instructions(instructions_raw)

    # created _instructions list of instruction objects
    # based on opcode string and arguments
    def _create_instructions(self,
                            instructions_raw: list[str, list[Argument]]) -> None:

        for opcode, args in instructions_raw:
            # dynamically create instruction object based on opcode string
            instruction_obj = getattr(InstructionsClass, opcode)(args)
            self._instructions.append(instruction_obj)

    def execute_instructions(self, memory: Memory) -> None:
        for instruction in self._instructions:
            instruction.execute(memory)

    def print_instructions(self):
        for instruction in self._instructions:
            print(instruction)


inpt = InputHandler()
inpt.parse_arguments()
inpt.parse_input()
inpt.convert_source()
inpt.verify_structure()

instructions = inpt.get_instructions()
# [print(x) for x in instructions]


"""
memory = Memory()
memory.create_frame()
memory.define_var("Gazdik", "TF")
memory.push_frame()


memory.create_frame()
memory.define_var("Cmorik", "TF")
memory.push_frame()


memory.create_frame()
memory.define_var("On", "TF")
memory.push_frame()

memory.pop_frame()
memory.define_var("On2", "TF")
memory.push_frame()

memory.define_var("On3", "LF")

memory.define_var("toto by malo byt v globalnom frame", "GF")

"""

memory = Memory()
interpreter = Interpreter(inpt.get_instructions())
interpreter.execute_instructions(memory) 

for x in memory.get_stack():
    print(x.variables)

x = memory.get_global_frame()
print(x.variables)
