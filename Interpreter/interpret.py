from input_handler import InputHandler
import re

inpt = InputHandler(debug=False)
inpt.parse_arguments()
inpt.parse_input()
inpt.convert_source()
inpt.verify_structure()
