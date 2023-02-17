import argparse
from lxml import etree


class Instruction:
    orders = set()
    def __init__(self, opcode: str):
        self.opcode = opcode

    @staticmethod
    def verify_instruction(instruction_xml, orders: set) -> bool:
        order = instruction_xml.get("order")
        if order is None:
            return False

        order = int(order)

        if order in orders or order <= 0:
            return False

        orders.add(order)

        return True

class InputHandler:
    def __init__(self, debug=False):
        self.args = {}
        self.source_file = None
        self.input_file = None
        self.instruction_orders = set()
        self.DEBUG = debug

    def parse_arguments(self):
        parser = argparse.ArgumentParser(add_help=False,
                                         prog="input_handler.py",
                                         description="Handle command line \
                                                 \arguments")

        parser.add_argument("--source", type=str, help="Specify source file")

        parser.add_argument("--input", type=str, help="Specify input file")

        parser.add_argument("--help", "--h", action="store_true",
                            help="Show this help message")

        # help message is generated automatically

        cmd_args = parser.parse_args()
        if cmd_args.help:
            # help can't be combined with any other arguments
            if cmd_args.source is not None or cmd_args.input is not None:
                if self.DEBUG:
                    print("Can't combine help with other arguments")
                exit(10)

            parser.print_help()
            exit(0)

        # at least one of these two must be present
        if cmd_args.source is None and cmd_args.input is None:
            if self.DEBUG:
                print("Missing one parameter")
            exit(10)

        self.args["source_file_parameter"] = cmd_args.source
        self.args["input_file_parameter"] = cmd_args.input

        if self.DEBUG:
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
            if self.DEBUG:
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
            if self.DEBUG:
                print(f"Exception {e} when reading source file {self.source_file}")

            exit(31)

    # verify the correct structure of xml, error 32
    def verify_structure(self):
        # check if there is any other element than program
        top_elements = self.source_file.xpath("/*")
        if len(list(top_elements)) != 1 or top_elements[0].tag != "program":
            if self.DEBUG:
                print("Missing program or more than one top level elements")
            exit(32)

        for element in self.source_file.xpath("/program/*"):
            if element.tag != "instruction":
                if self.DEBUG:
                    print("Other element than instruction found in <program>")
                exit(32)

            if not Instruction.verify_instruction(element, self.instruction_orders):
                if self.DEBUG:
                    print("Failed to verify instruction")

                exit(32)

            # print(etree.tostring(element))
