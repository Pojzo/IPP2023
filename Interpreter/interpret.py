from input_handler import InputHandler

inpt = InputHandler(debug=False)
inpt.parse_arguments()
inpt.parse_input()
inpt.convert_source()

if inpt.DEBUG:
    print(f"{inpt.input_file=}")
    print(f"{inpt.source_file=}")
