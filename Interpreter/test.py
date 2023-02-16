import unittest
import pytest
import subprocess
import os
import sys
import tempfile


# run program and returns its output and return code
def run_program(arguments: list[str],
                input_string: str) -> list[str, int]:

    full_arguments = ["py", "interpret.py"] + arguments
    result = subprocess.run(full_arguments,
                            input=input_string,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    return type("result", (),
                {"stdout": result.stdout.decode(),
                 "return_code": result.returncode,
                 "stderr": result.stderr.decode()})


class TestInterpreter(unittest.TestCase):
    def test_no_parameters(self):
        result = run_program([], "")
        assert(result.stdout == "")
        assert(result.return_code == 10)

    def test_only_help(self):
        result = run_program(["--help"], "")
        assert(result.stdout != "")
        assert(result.return_code == 0)

    def test_help_with_input(self):
        result = run_program(["--help", "--input=file]"], "")
        assert(result.stdout == "")
        assert(result.return_code == 10)

    def test_help_with_source(self):
        result = run_program(["--help", "--source=file]"], "")
        assert(result.stdout == "")
        assert(result.return_code == 10)

    def test_help_input_source(self):
        result = run_program(["--help", "--input=file]", "--source=file2"],
                             "")
        assert(result.stdout == "")
        assert(result.return_code == 10)

    def test_non_existing_file(self):
        result = run_program(["--source=jldskdsjfhdsfkjhsdfsodjfhdsfjids",
                              "--input=sdlkjfdslkfjslkfj"], "")
        assert(result.stdout == "")
        assert(result.return_code == 11)

    def test_existing_file(self):
        os.system("touch temp1")
        os.system("touch temp2")
        result = run_program(["--source=temp1", "--input=temp2"], "")
        assert(result.stdout == "")
        assert(result.return_code == 0)


def remove_file(x):
    if os.path.exists(x):
        os.remove(x)


if __name__ == "__main__":
    unittest.main(verbosity=3)
    remove_file("temp1")
    remove_file("temp2")
