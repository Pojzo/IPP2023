from input_handler import InputHandler
from input_handler import Argument
from memory import Memory
import instructions as InstructionsClass
from config import DEBUG
from debug import DEBUG_PRINT
from error_codes import ErrorCodes

import sys


# the interpreter gets list of lines from input handler
class Interpreter:
    def __init__(self, instructions_raw: list[str, list[Argument]]):
        self._instruction_index = 0
        self._instructions = []
        self._labels_indeces = {}
        self._create_labels(instructions_raw)
        self._create_instructions(instructions_raw)
        InstructionsClass.Instruction.instruction_index_callback = self.get_instruction_index
        # [print(x) for x in self._instructions]

    
    def get_instruction_index(self) -> int:
        return self._instruction_index

    def _create_labels(self, instructions_raw: list[str, list[Argument]]) -> None:
        for index, (opcode, args) in enumerate(instructions_raw):
            if opcode == "LABEL":
                # duplicate label
                if args[0].value in self._labels_indeces:
                    DEBUG_PRINT("Duplicate label")
                    exit(ErrorCodes.InputSemanticsBad)

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
        self._instruction_index = 0
        while self._instruction_index < len(self._instructions):
            label = self._instructions[self._instruction_index].execute(memory)
            if label is None:
                self._instruction_index += 1
                continue

            if type(label) == str:
                if label not in self._labels_indeces:
                    DEBUG_PRINT("Label doesn't exist")
                    exit(ErrorCodes.InputSemanticsBad)

                self._instruction_index = self._labels_indeces[label]

            elif type(label) == int:
                self._instruction_index = label
            else:
                # this should never happen
                print(type(label))
                print("DFDSFSFDSAFASFADSFSF neni dobre")


    def print_instructions(self):
        for instruction in self._instructions:
            print(instruction)


inpt = InputHandler()
inpt.parse_arguments()
inpt.parse_input()
inpt.convert_source()
inpt.verify_structure()

memory = Memory()
instructions, input_file = inpt.get_instructions()
if input_file == "stdin":
    input_stream = sys.stdin
else:
    input_stream = open(input_file, 'r')

InstructionsClass.Instruction.input_stream = input_stream
interpreter = Interpreter(instructions)
interpreter.execute_instructions(memory) 

exit(0)
