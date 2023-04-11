from input_handler import InputHandler
from input_handler import Argument
from memory import Memory
import instructions as InstructionsClass
from config import DEBUG


# the interpreter gets list of lines from input handler
class Interpreter:
    def __init__(self, instructions_raw: list[str, list[Argument]]):
        self._instructions = []
        self._labels_indeces = {}
        self._create_labels(instructions_raw)
        self._create_instructions(instructions_raw)
        # [print(x) for x in self._instructions]


    def _create_labels(self, instructions_raw: list[str, list[Argument]]) -> None:
        for index, (opcode, args) in enumerate(instructions_raw):
            if opcode == "LABEL":
                self._labels_indeces[args[0].value] = index


    # created _instructions list of instruction objects
    # based on opcode string and arguments
    def _create_instructions(self,
                            instructions_raw: list[str, list[Argument]]) -> None:

        for opcode, args in instructions_raw:
            # dynamically create instruction object based on opcode string
            instruction_obj = getattr(InstructionsClass, opcode)(args)
            self._instructions.append(instruction_obj)

    def execute_instructions(self, memory: Memory) -> None:
        index = 0
        while index < len(self._instructions):
            label = self._instructions[index].execute(memory)
            if label is None:
                index += 1
                continue

            index = self._labels_indeces[label]

    def print_instructions(self):
        for instruction in self._instructions:
            print(instruction)


inpt = InputHandler()
inpt.parse_arguments()
inpt.parse_input()
inpt.convert_source()
inpt.verify_structure()

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

memory.define_var("global", "GF")
memory.set_var("global", "GF", "gazdik", 3)

memory.move_var("global", "GF", "On3", "LF")
"""

memory = Memory()
interpreter = Interpreter(inpt.get_instructions())
interpreter.execute_instructions(memory) 

exit(0)

# local_frame = memory.get_frame_stack()[-1]
local_frame = []
for frame in memory.get_frame_stack():
    print(frame)
    for name in frame.variables:
        variable = frame.variables[name]
        print(f"{variable.name=}")
        print(f"{variable.value=}")
        print(f"{variable.datatype=}")
        print()

print("Global frame: ")
for name in memory._global_frame.variables:
    variable = memory._global_frame.variables[name]
    print(f"{variable.name=}")
    print(f"{variable.value=}")
    print(f"{variable.datatype=}")
    print()
