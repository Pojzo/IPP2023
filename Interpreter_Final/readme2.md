Implementační dokumentace k 2. úloze do IPP 2022/2023

Jméno a příjmení: Peter Kováč

Login: xkovac66

# File structure
- *interpret.py_* 
	- `class Interpter()`
-  *input_handler.py* 
	- `class InputHandler() `
	- `class ArgumentType(Enum)`
	- `class Argument()`
	
- *memory.py*
	- `class Variable()`
	- `class DataType(Enum)`
	-  `class Frame()`
	-  `class Memory()`

- *instructions.py*
    -  `class Instruction(@abstract)`
	-  `class ArithmeticInstruction(Instruction)`
	-  `class ArithmeticStackInstruction(Instruction)`
    -  `class ConvertInstruction(Instruction)`
    -  `class JumpInstruction(Instruction)`
  
- *error_codes.py*
	- `class ErrorCodes(Enum)`
	
- *debug.py_*



# Implementation

## Handling input
When either the `--input` or `--source` aren't supplied, input file or source file, respectively, are loaded from the standard input, otherwise read from a file. `InputHandler()` is responsible for checking if the source file has a valid structure, checking whether all *instructions* and *arguments* are in the correct format and order. Errors 31 and 32 are thrown if there's anything wrong with the source file. For parsing the input xml, lxml library is used.

## Storing instructions
To make the implementation easier, arguments are stored in the `Argument` class, which contains the `type`,` value` and the` datatype`, if dealing with constants. The `Interpret` class calls the function `get_instructions()`, which returns the instructions in the correct order, along with their arguments.  
The `_create_instruction()` method takes care of dynamically creating instruction objects based on their name. Every instruction class is named after its opcode.
```py
instruction_obj = getattr(InstructionsClass, opcode)(args)
```

## Execution
The `execute_instructions()` method takes care of executing instructions, and handles jumps. It runs in a while loop and ends when the last instruction is executed. The `Instruction()` class inherits from `abc.ABC` and defines an abstract method `execute()`, as every instruction needs to have a separate implementation. 
```py
import abc

class Instruction(abc.ABC):
	# methods
	...
	@abc.abstractmethod
	def execute(self) -> None:
		pass

```

Some instructions, such as arithmetic ones do have a similar implementation, so creating a `ArithmeticInstruction(Instruction)` sublclass helped to abide by the *DRY* principle. For the bonus implementation of stack operations, the `ArithmeticStackInstruction(Instruction)` class was created, which is similar to ArithmeticInstruction, but doesn't require any input arguments. There is also `ConvertInstruction(Instruction)` and `JumpInstruction(Instruction)` subclasses.

```py
# inherit from Instruction
class ArithmeticInstruction(Instruction):
	def __init__(self, opcode: str, args: list[Argument):
		super().__init__(opcode, args)
		
def execute(self, function_name: str) -> None:
	# call the corresponding function in Memory

# inherit from ArithmeticInstruction
class ADD(ArithmeticInstruction):
	def __init__(self, args: list[Argument]):
		super().__init__(self.__class__.__name__, args)
		
	def execute(self) -> None:
		super().execute("add")
```

Each arithmetic operation has a corresponding function in the `Memory()` class and is called based on the `function_name`argument.

## Memory
The `Memory()` class is implemented as a singleton to ensure only one instance and ease of access in the global scope. Creating a singleton in python is a bit tricky, but it's possible using a metaclass, which returns the single instance of a class if it exists, and if not, then it creates one.

```py
class Singleton(type):
	_instances = {}
	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class Memory(metaclass=Singleton):
	# ...
```
Memory serves as an API for the instructions to access the different frames - Global, Local and Temporary frame. The `Frame` class is used to store and retrieve variables in memory. The most used methods include 
```py
# return a variable, if it doesn't exist, exit with an error
def get_var(self, name: str, frame: str) -> Variable:

# define a variable in a frame
# it doesn't yet have a value and a datatype
# exit with an error if it's already defined
def define(self, name: str, frame: str) -> None:

# set the value and datatype for a variable
# exit with an error if it's not initialized
def set_var(self, name: str, frame: str, value: str, datatype: Datatype) -> None:
```

Memory also contain methods for arithmetic instructions, which check if supplied variables are of adequate datatype for the specific instruction. When an instruction pushes its argument to the stack, they are popped by a method in memory and depending whether `stack_only` is set to true, the result is either written into the destination variable, or pushed onto the stack.

## Worth mentioning
Throughout the program, various enums were used to make the code more readable. 

Enum for the datatype of a variable or a constant
```py
class DataType(Enum):
	TYPE_INT    = 1
	TYPE_STRING = 2
	TYPE_BOOL   = 3
	TYPE_NIL    = 4
	TYPE_FLOAT  = 5
```
Enum for the `type` attribute in an instruction
```py
class ArgumentType(Enum):
	LABEL = 1
	TYPE  = 2
	VAR   = 3
	SYMB  = 4
```
Enum for storing error codes
```py
	class ErrorCodes(Enum):
		InputNotWellFormed = 31
		InputStructureBad  = 32
		InputSemanticsBad  = 52
		OperandTypeBad     = 53
		VariableNotDefined = 54
		FrameNotDefined    = 55
		MissingValue       = 56
		OperandValueBad    = 57
		StringError        = 58	
```

For debugging purposes, a `DEBUG_PRINT("message")`  is added before every `exit()`. The `DEBUG_PRINT()` function only prints the message if `DEBUG` variable is set to true. This makes it very easy to run the program in testing and debugging mode.

# Testing
For testing purposes, there is `test.py` file which tests a directory with multiple categories of tests. A test consists of feeding the program with appropriate source file, input file and is responsible for determining whether the return code and output of the program is correct. The test script lets the user know whether the test is successful. If it isn't, it tells the user what's wrong, either the return code or the output. If there is a mismatch in output, the correct one is printed alongside with the one returned by the program.


