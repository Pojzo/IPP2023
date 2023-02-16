import argparse


class Input:
    def __init__(self, debug=False):
        self.args = {}
        self.source_file = None
        self.input_file = None
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
