from input_handler import InputHandler
from input_handler import ArgumentType
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
                'CREATEFRAME': self.create_frame,
                'PUSHFRAME': self.push_frame,
                'POPFRAME': self.pop_frame,
                'DEFVAR': self.defvar,
                'CALL': self.call,
                'RETURN': self.return_,
                'PUSHS': self.pushs,
                'POPS': self.pops,
                'ADD': self.add,
                'SUB': self.sub,
                'MUL': self.mul,
                'IDIV': self.idiv,
                'LT': self.lt,
                'GT': self.gt,
                'EQ': self.eq,
                'AND': self.and_,
                'OR': self.or_,
                'NOT': self.not_,
                'INT2CHAR': self.int2char,
                'STRI2INT': self.stri2int,
                'READ': self.read,
                'WRITE': self.write,
                'CONCAT': self.concat,
                'STRLEN': self.strlen,
                'GETCHAR': self.getchar,
                'SETCHAR': self.setchar,
                'TYPE': self.type_,
                'LABEL': self.label,
                'JUMP': self.jump,
                'JUMPIFEQ': self.jumpifeq,
                'JUMPIFNEQ': self.jumpifneq,
                'EXIT': self.exit,
                'DPRINT': self.dprint,
                'BREAK': self.break_
                }


    def move(self):
        # code to run the interpreter

    def create_frame(self):
        # code to create a new frame

    def push_frame(self):
        # code to push the current frame to the stack

    def pop_frame(self):
        # code to pop the top frame from the stack and set it as the current frame

    def defvar(self, var):
        # code to define a variable

    def call(self, label):
        # code to call a subroutine at the specified label

    def return_(self):
        # code to return from a subroutine

    def pushs(self, value):
        # code to push a value onto the stack

    def pops(self, var):
        # code to pop a value from the stack and store it in a variable

    def add(self, var, left, right):
        # code to add two values and store the result in a variable

    def sub(self, var, left, right):
        # code to subtract one value from another and store the result in a variable

    def mul(self, var, left, right):
        # code to multiply two values and store the result in a variable

    def idiv(self, var, left, right):
        # code to integer divide one value by another and store the result in a variable

    def lt(self, var, left, right):
        # code to compare two values and store the result of a less-than comparison in a variable

    def gt(self, var, left, right):
        # code to compare two values and store the result of a greater-than comparison in a variable

    def eq(self, var, left, right):
        # code to compare two values and store the result of an equality comparison in a variable

    def and_(self, var, left, right):
        # code to perform a logical AND operation on two values and store the result in a variable

    def or_(self, var, left, right):
        # code to perform a logical OR operation on two values and store the result in a variable

    def not_(self, var, value):
        # code to perform a logical NOT operation on a value and store the result in a variable

    def int2char(self, var, value):
        # code to convert an integer to a character and store the result in a variable

    def stri2int(self, var, string, index):
        # code to get the ASCII code of a character in a string and store the result in a variable

    def read(self, var, type_):
        # code to read a value from standard input and store it in a variable

    def write(self, value):
        # code to write a value to standard output

    def concat(self, var, left, right):
        # code to concatenate two strings and store the result in a variable

    def strlen(self, var, value):
        # code to get the length of a string and store the result in a variable

    def getchar(self, var, string, index):
        # code to get a character from a string and store it in a variable

    def setchar(self, string, index, value):
        # code to set a character in a string to a new value

    def type_(self, var, value):
        # code to get the type of a value and store it in a variable

    def label(self, label):
        # code to create a label

    def jump(self, label):
        # code to jump to a label

    def jumpifeq(self, label, left, right):
        # code to jump to a label if two values are equal

    def jumpifneq(self, label, left, right):
        # code to jump to a label if two values are not equal

    def exit(self, code):
        # code to exit the program

    def dprint(self, value):
        # code to print a value to standard error

    def break_(self):
        # code to stop execution of the program
