from input_handler import Input

inpt = Input(debug=False)
inpt.parse_arguments()
inpt.parse_input()

if inpt.DEBUG:
    print(f"{inpt.input_file=}")
    print(f"{inpt.source_file=}")
