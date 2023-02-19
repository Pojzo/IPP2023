from input_handler import InputHandler
from memory import Memory


inpt = InputHandler()
inpt.parse_arguments()
inpt.parse_input()
inpt.convert_source()
inpt.verify_structure()


class Intepreter:
    def __init__(self):
        self._memory = Memory()
        self._opcode_func = {
                'MOVE': self.move,
                }
