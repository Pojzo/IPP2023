import argparse
from lxml import etree
from enum import Enum
from error_codes import ErrorCodes
from config import DEBUG
import re


class ArgumentType(Enum):
    LABEL = 1
    SYMBOL = 2
    VARIABLE = 3
    TYPE = 4

    def __str__(self):
        return self.name


class Argument:
    def __init__(self, arg_type: ArgumentType, value: str):
        self.__type = arg_type
        self.__value = value

    def __repr__(self):
        return f"type: {self.__type} value: {self.__value}"


# dictionary mappings where key is the name of instruction and
# value is an array of arguments to that instruction
# bruh this looks ugly as hell but it does the job (hopefully)
instructions_dic = {
        "MOVE": [ArgumentType.VARIABLE, ArgumentType.SYMBOL],
        "CREATEFRAME": [],
        "PUSHFRAME": [],
        "POPFRAME": [],
        "DEFVAR": [ArgumentType.VARIABLE],
        "CALL": [ArgumentType.LABEL],
        "RETURN": [],
        "PUSHS": [ArgumentType.SYMBOL],
        "POPS": [ArgumentType.VARIABLE],
        "ADD": [ArgumentType.VARIABLE, ArgumentType.SYMBOL,
                ArgumentType.SYMBOL],
        "SUB": [ArgumentType.VARIABLE, ArgumentType.SYMBOL,
                ArgumentType.SYMBOL],
        "MUL": [ArgumentType.VARIABLE, ArgumentType.SYMBOL,
                ArgumentType.SYMBOL],
        "IDIV": [ArgumentType.VARIABLE, ArgumentType.SYMBOL,
                 ArgumentType.SYMBOL],
        "LT": [ArgumentType.VARIABLE, ArgumentType.SYMBOL,
               ArgumentType.SYMBOL],
        "GT": [ArgumentType.VARIABLE, ArgumentType.SYMBOL,
               ArgumentType.SYMBOL],
        "EQ": [ArgumentType.VARIABLE, ArgumentType.SYMBOL,
               ArgumentType.SYMBOL],
        "AND": [ArgumentType.VARIABLE, ArgumentType.SYMBOL,
                ArgumentType.SYMBOL],
        "OR": [ArgumentType.VARIABLE, ArgumentType.SYMBOL,
               ArgumentType.SYMBOL],
        "NOT": [ArgumentType.VARIABLE, ArgumentType.SYMBOL],
        "INT2CHAR": [ArgumentType.VARIABLE, ArgumentType.SYMBOL],
        "STRI2INT": [ArgumentType.VARIABLE, ArgumentType.SYMBOL,
                     ArgumentType.SYMBOL],
        "READ": [ArgumentType.VARIABLE, ArgumentType.TYPE],
        "WRITE": [ArgumentType.SYMBOL],
        "CONCAT": [ArgumentType.VARIABLE, ArgumentType.SYMBOL,
                   ArgumentType.SYMBOL],
        "STRLEN": [ArgumentType.VARIABLE, ArgumentType.SYMBOL],
        "GETCHAR": [ArgumentType.VARIABLE, ArgumentType.SYMBOL,
                    ArgumentType.SYMBOL],
        "SETCHAR": [ArgumentType.VARIABLE, ArgumentType.SYMBOL,
                    ArgumentType.SYMBOL],
        "TYPE": [ArgumentType.VARIABLE, ArgumentType.SYMBOL],
        "LABEL": [ArgumentType.LABEL],
        "JUMP": [ArgumentType.LABEL],
        "JUMPIFEQ": [ArgumentType.LABEL, ArgumentType.SYMBOL,
                     ArgumentType.SYMBOL],
        "JUMPIFNEQ": [ArgumentType.LABEL, ArgumentType.SYMBOL,
                      ArgumentType.SYMBOL],
        "EXIT": [ArgumentType.SYMBOL],
        "DPRINT": [ArgumentType.SYMBOL],
        "BREAK": [],
        # bonus
        "CLEARS": [],
        "ADDS": [ArgumentType.VARIABLE, ArgumentType.SYMBOL, ArgumentType.SYMBOL],
        "SUBS": [ArgumentType.VARIABLE, ArgumentType.SYMBOL, ArgumentType.SYMBOL],
        "MULS": [ArgumentType.VARIABLE, ArgumentType.SYMBOL, ArgumentType.SYMBOL],
        "IDIVS": [ArgumentType.VARIABLE, ArgumentType.SYMBOL, ArgumentType.SYMBOL],
        "LTS": [ArgumentType.VARIABLE, ArgumentType.SYMBOL, ArgumentType.SYMBOL],
        "GTS": [ArgumentType.VARIABLE, ArgumentType.SYMBOL, ArgumentType.SYMBOL],
        "EQS": [ArgumentType.VARIABLE, ArgumentType.SYMBOL, ArgumentType.SYMBOL],
        "ANDS": [ArgumentType.VARIABLE, ArgumentType.SYMBOL, ArgumentType.SYMBOL],
        "ORS": [ArgumentType.VARIABLE, ArgumentType.SYMBOL, ArgumentType.SYMBOL],
        "NOTS": [ArgumentType.VARIABLE, ArgumentType.SYMBOL],
        "INT2CHARS": [],
        "STRI2INTS": [],
        "JUMPIFEQS": [],
        "JUMPIFNEQS": [],
}


class InstructionVerify:
    @staticmethod
    def verify_instruction(instruction_xml, orders: set) -> bool:
        order = instruction_xml.get("order")
        if order is None:
            if DEBUG:
                print("Missing order of instruction")
            return False

        order = int(order)

        # checks whether order is correct, must be greater
        # than zero and in the correct order
        if order <= 0 or order in orders:
            if DEBUG:
                print("Wrong order of instruction")
            return False

        orders.add(order)
        opcode = instruction_xml.get("opcode")
        # check for missing opcode
        if opcode is None:
            if DEBUG:
                print("Missing opcode")
            return False

        # check for wrong(unknown) opcode
        if opcode not in instructions_dic:
            if DEBUG:
                print("Wrong opcode")
            return False

        # get all children of instruction
        expected_num_args = len(instructions_dic[opcode])
        arg_numbers = set()
        for index, child in enumerate(instruction_xml.iterchildren()):
            # check if arg matches arg<digit> using regex
            if not re.match(r"arg[0-9]+", child.tag) or int(child.tag[3:]) in arg_numbers:
                if DEBUG:
                    print(f"Failed to verify arguments {child.tag}")
                return False

            arg_numbers.add(int(child.tag[3:]))

        return len(arg_numbers) == expected_num_args


class InputHandler:
    def __init__(self):
        self.args = {}
        self.source_file = None
        self.input_file = None
        self.instruction_orders = set()
        DEBUG = False

    def parse_arguments(self):
        parser = argparse.ArgumentParser(add_help=False,
                                         prog="input_handler.py",
                                         description="Handle command line \
                                                 \arguments")

        parser.add_argument("--source", type=str, help="Specify source file")

        parser.add_argument("--input", type=str, help="Specify input file")

        parser.add_argument("--help", "--h", action="store_true",
                            help="Show this help message")

        parser.add_argument("--debug", "--d", action="store_true",
                            help="Enable debug mode")

        # help message is generated automatically

        cmd_args = parser.parse_args()

        if cmd_args.help:
            # help can't be combined with any other arguments
            if cmd_args.source is not None or cmd_args.input is not None:
                if DEBUG:
                    print("Can't combine help with other arguments")
                exit(10)

            parser.print_help()
            exit(0)

        # at least one of these two must be present
        if cmd_args.source is None and cmd_args.input is None:
            if DEBUG:
                print("Missing one parameter")
            exit(10)

        self.args["source_file_parameter"] = cmd_args.source
        self.args["input_file_parameter"] = cmd_args.input

        if DEBUG:
            print(f"{self.args['source_file_parameter']=}")
            print(f"{self.args['input_file_parameter']=}")

    # open file and return its contents as string
    def load_file(self, file_name: str) -> str:
        try:
            file = open(file_name)
            file_content = file.read()
            file.close()
            return file_content

        # catch an exception when opening file
        except Exception as e:
            if DEBUG:
                print(f"Error when opening input file {e=} {file_name=}")
            exit(11)

    # load input to self.source_file and self.input_file
    # throw appropriate error if a problem is encountered
    def parse_input(self):
        if self.args["input_file_parameter"] is not None:
            self.input_file = self.load_file(self.args["input_file_parameter"])

        else:
            self.input_file = input()

        if self.args["source_file_parameter"] is not None:
            self.source_file = self.load_file(
                    self.args["source_file_parameter"])
        else:
            self.source_file = input()

    # convert source file to xml
    def convert_source(self):
        try:
            self.source_file = etree.fromstring(self.source_file.encode())
        except Exception as e:
            if DEBUG:
                print(f"Exception {e} when reading source file {self.source_file}")

            exit(ErrorCodes.InputNotWellFormed)

    # verify the correct structure of xml, error ErrorCodes.InputStructureBad
    def verify_structure(self):
        # check if there is any other element than program
        top_elements = self.source_file.xpath("/*")
        if len(list(top_elements)) != 1 or top_elements[0].tag != "program":
            if DEBUG:
                print("Missing program or more than one top level elements")
            exit(ErrorCodes.InputStructureBad)

        for element in self.source_file.xpath("/program/*"):
            if element.tag != "instruction":
                if DEBUG:
                    print("Other element than instruction found in <program>")
                exit(ErrorCodes.InputStructureBad)

            # could've chosen a better name but whatever
            if not InstructionVerify.verify_instruction(
                    element, self.instruction_orders):

                if DEBUG:
                    print("Failed to verify instruction", etree.tostring(element))

                exit(ErrorCodes.InputStructureBad)
            # print(etree.tostring(element))

    # return the instruction in the format
    # [opcode, [arg1, arg2, ...]] 
    def get_instructions(self) -> list[str, list[Argument]]:
        instructions = []
        for instruction in self.source_file.xpath("/program/*"):
            opcode = instruction.get("opcode")
            arguments = []
            for argument in instruction.iterchildren():
                arg_type = argument.get("type")
                arg_value = argument.text
                arguments.append(Argument(arg_type, arg_value))

            instructions.append([opcode, arguments])

        return instructions
