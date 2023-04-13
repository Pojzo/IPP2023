import argparse
from lxml import etree
from enum import Enum
from error_codes import ErrorCodes
from debug import DEBUG_PRINT
import re
import sys


class ArgumentType(Enum):
    LABEL = 1
    TYPE = 2
    VAR = 3
    SYMB = 4

    @staticmethod
    def convert_to_enum(arg_type: str) -> "ArgumentType":
        if arg_type == "label":
            return ArgumentType.LABEL
        elif arg_type == "var":
            return ArgumentType.VAR
        elif arg_type == "type":
            return ArgumentType.TYPE
        else:
            return ArgumentType.SYMB


    def __str__(self):
        return self.name

class Argument:
    def __init__(self, arg_type: ArgumentType, value: str, datatype=None):
        self.type_ = arg_type
        self.value = value
        # only for symbols
        self.datatype = datatype

    def __repr__(self):
        return f"type: {self.type_} value: {self.value} datatype: {self.datatype}"


# dictionary mappings where key is the name of instruction and
# value is an array of arguments to that instruction
# bruh this looks ugly as hell but it does the job (hopefully)
instructions_dic = {
        "MOVE": [ArgumentType.VAR, ArgumentType.SYMB],
        "CREATEFRAME": [],
        "PUSHFRAME": [],
        "POPFRAME": [],
        "DEFVAR": [ArgumentType.VAR],
        "CALL": [ArgumentType.LABEL],
        "RETURN": [],
        "PUSHS": [ArgumentType.SYMB],
        "POPS": [ArgumentType.VAR],
        "ADD": [ArgumentType.VAR, ArgumentType.SYMB,
                ArgumentType.SYMB],
        "SUB": [ArgumentType.VAR, ArgumentType.SYMB,
                ArgumentType.SYMB],
        "MUL": [ArgumentType.VAR, ArgumentType.SYMB,
                ArgumentType.SYMB],
        "IDIV": [ArgumentType.VAR, ArgumentType.SYMB,
                 ArgumentType.SYMB],
        "LT": [ArgumentType.VAR, ArgumentType.SYMB,
               ArgumentType.SYMB],
        "GT": [ArgumentType.VAR, ArgumentType.SYMB,
               ArgumentType.SYMB],
        "EQ": [ArgumentType.VAR, ArgumentType.SYMB,
               ArgumentType.SYMB],
        "AND": [ArgumentType.VAR, ArgumentType.SYMB,
                ArgumentType.SYMB],
        "OR": [ArgumentType.VAR, ArgumentType.SYMB,
               ArgumentType.SYMB],
        "NOT": [ArgumentType.VAR, ArgumentType.SYMB],
        "INT2CHAR": [ArgumentType.VAR, ArgumentType.SYMB],
        "STRI2INT": [ArgumentType.VAR, ArgumentType.SYMB,
                     ArgumentType.SYMB],
        "READ": [ArgumentType.VAR, ArgumentType.TYPE],
        "WRITE": [ArgumentType.SYMB],
        "CONCAT": [ArgumentType.VAR, ArgumentType.SYMB,
                   ArgumentType.SYMB],
        "STRLEN": [ArgumentType.VAR, ArgumentType.SYMB],
        "GETCHAR": [ArgumentType.VAR, ArgumentType.SYMB,
                    ArgumentType.SYMB],
        "SETCHAR": [ArgumentType.VAR, ArgumentType.SYMB,
                    ArgumentType.SYMB],
        "TYPE": [ArgumentType.VAR, ArgumentType.SYMB],
        "LABEL": [ArgumentType.LABEL],
        "JUMP": [ArgumentType.LABEL],
        "JUMPIFEQ": [ArgumentType.LABEL, ArgumentType.SYMB,
                     ArgumentType.SYMB],
        "JUMPIFNEQ": [ArgumentType.LABEL, ArgumentType.SYMB,
                      ArgumentType.SYMB],
        "EXIT": [ArgumentType.SYMB],
        "DPRINT": [ArgumentType.SYMB],
        "BREAK": [],
        # bonus
        "CLEARS": [],
        "ADDS": [],
        "SUBS": [],
        "MULS": [],
        "IDIVS": [],
        "LTS": [],
        "GTS": [],
        "EQS": [],
        "ANDS": [],
        "ORS": [],
        "NOTS": [],
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
            DEBUG_PRINT("Missing order of instruction")
            return False

        try:
            order = int(order)
        except:
            DEBUG_PRINT("Wrong order of instruction")
            exit(ErrorCodes.InputStructureBad)

        # checks whether order is correct, must be greater
        # than zero and in the correct order
        if order <= 0 or order in orders:
            DEBUG_PRINT("Wrong order of instruction")
            return False

        orders.add(order)
        opcode = instruction_xml.get("opcode")
        # check for missing opcode
        if opcode is None:
            DEBUG_PRINT("Missing opcode")
            return False

        # check for wrong(unknown) opcode
        if opcode.upper() not in instructions_dic:
            DEBUG_PRINT("Wrong opcode")
            return False

        # get all children of instruction
        expected_num_args = len(instructions_dic[opcode.upper()])
        arg_numbers = set()
        for index, child in enumerate(instruction_xml.iterchildren()):
            # check if arg matches arg<digit> using regex
            if not re.match(r"arg[0-9]+", child.tag) or int(child.tag[3:]) in arg_numbers:
                DEBUG_PRINT(f"Failed to verify arguments {child.tag}")
                return False
            
            arg_numbers.add(int(child.tag[3:]))

        # check if it matches the numbers
        if not all([x in arg_numbers for x in range(1, expected_num_args + 1)]):
            DEBUG_PRINT("Missing argument or wrong order")
            return False

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
                DEBUG_PRINT("Can't combine help with other arguments")
                exit(10)

            parser.print_help()
            exit(0)

        # at least one of these two must be present
        if cmd_args.source is None and cmd_args.input is None:
            DEBUG_PRINT("Missing one parameter")
            exit(10)

        self.args["source_file_parameter"] = cmd_args.source
        self.args["input_file_parameter"] = cmd_args.input

        # DEBUG_PRINT(f"{self.args['source_file_parameter']=}")
        # DEBUG_PRINT(f"{self.args['input_file_parameter']=}")

    # open file and return its contents as string
    def load_file(self, file_name: str) -> str:
        try:
            file = open(file_name)
            file_content = file.read()
            file.close()
            return file_content

        # catch an exception when opening file
        except Exception as e:
            print(e)
            DEBUG_PRINT(f"Error when opening input file {e=} {file_name=}")
            exit(11)

    # load input to self.source_file and self.input_file
    # throw appropriate error if a problem is encountered
    def parse_input(self):
        if self.args["input_file_parameter"] is not None:
            self.input_file = self.args["input_file_parameter"]

        else:
            self.input_file = "stdin"

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
            DEBUG_PRINT(f"Exception {e} when reading source file {self.source_file}")

            exit(ErrorCodes.InputNotWellFormed)

    # verify the correct structure of xml, error ErrorCodes.InputStructureBad
    def verify_structure(self):
        # check if there is any other element than program
        top_elements = self.source_file.xpath("/*")
        if len(list(top_elements)) != 1 or top_elements[0].tag != "program":
            DEBUG_PRINT("Missing program or more than one top level elements")
            exit(ErrorCodes.InputStructureBad)

        for element in self.source_file.xpath("/program/*"):
            if element.tag != "instruction":
                DEBUG_PRINT("Other element than instruction found in <program>")
                exit(ErrorCodes.InputStructureBad)

            # could've chosen a better name but whatever
            if not InstructionVerify.verify_instruction(
                    element, self.instruction_orders):

                DEBUG_PRINT("Failed to verify instruction" + str(etree.tostring(element)))

                exit(ErrorCodes.InputStructureBad)
            # print(etree.tostring(element))



    # return the instruction in the format
    # [opcode, [arg1, arg2, ...]]
    def get_instructions(self) -> list[str, list[Argument]]:
        instructions = []
        for instruction in self.source_file.xpath("/program/*"):
            opcode = instruction.get("opcode").upper()
            arguments = []
            for argument in instruction.iterchildren():
                arg_type = ArgumentType.convert_to_enum(argument.get("type"))
                arg_value = argument.text
                argument_order = int(argument.tag[3])
                if arg_type == ArgumentType.SYMB:
                    argument = Argument(arg_type, arg_value, datatype=argument.get("type"))
                else:
                    argument = Argument(arg_type, arg_value)

                arguments.append([argument, argument_order])

            instruction_order = int(instruction.get("order"))

            arguments.sort(key=lambda x: x[1]) 
            arguments = [x[0] for x in arguments]
            instructions.append([instruction_order, opcode, arguments])

        instructions.sort(key=lambda x: x[0])
        
        # return just the opcode and arguments
        return [x[1:] for x in instructions], self.input_file

