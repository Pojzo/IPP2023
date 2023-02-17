import os
import glob
import argparse
import subprocess
import multiprocessing
import difflib
import os

from collections import defaultdict

BLUE = "\033[34m"
BLACK = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"

TEST_DIR = "./interpret_tests"

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", "--v", default="1")

args = parser.parse_args()

test_dic = defaultdict(list)



class Test():
    def __init__(self, dirname: str, testname: str,
                 expected_output: str, expected_return_code: str,
                 stdout: str, stderr: str, return_code, src,
                 test_num: int):

        self.dirname = dirname
        self.testname = testname
        self.src = src
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = int(return_code)
        self.expected_output = expected_output
        self.expected_return_code = int(expected_return_code)
        self.test_num = test_num
        self.passed = True
        self.return_code_passed = True
        self.diff = ""

    def check_if_passed(self):
        diff = difflib.unified_diff([line.strip() for line in self.stdout.splitlines()], [line.strip() for line in
                                                                                          self.expected_output.splitlines()], lineterm='', n=0)
        if self.return_code != self.expected_return_code:
            self.return_code_passed = False

        diff = "\n".join(list(diff))
        if len(diff):
            self.diff = diff
            self.passed = False

    def print_test(self):
        num_dir_tests = num_files[self.dirname]
        if self.stderr and args.verbose:
            print(self.stderr)

        if self.passed:
            if not self.return_code_passed:

                print(f"{RED} Test [{self.test_num}/{num_dir_tests}] {self.testname} unsuccessfull (wrong return code) {BLACK}")
                if int(args.verbose) == 1:
                    print(self.src)
                
                print()
                print(f"{RED} Expected return code {self.expected_return_code} got {self.return_code} {BLACK}")
                print("---------------------------------")
                print()
            else:
                print(f"{GREEN} Test [{self.test_num}/{num_dir_tests}] {self.testname} successful {BLACK}")
                print("---------------------------------")


        else:
            print(f"{RED} Test [{self.test_num}/{num_dir_tests}] {self.testname} unsuccessfull (wrong output) {'+ (wrong return code)' if not self.return_code_passed else ''}{BLACK}")

            if int(args.verbose) == 1:
                print(self.src)
                print("Expected output:")
                print(self.expected_output)
                print()
                print("Program output:")
                print(self.stdout)
                print(self.diff)

            if not self.return_code_passed:
                # print("=================================")
                print(f"{RED} Expected return code {self.expected_return_code} got {self.return_code} {BLACK}")

            print("---------------------------------")

def run_program(file_name: str, num_test: int) -> Test:
    command = f"py interpret.py --source={file_name}.src \
            --input={file_name}.in"

    program = subprocess.run(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             encoding="utf-8",
                             shell=True)

    if not os.path.exists(f"{file_name}.out"):
        expected_output = ""
    else:
        with open(f"{file_name}.out", "r") as file:
            expected_output = file.read()

    with open(f"{file_name}.rc", "r") as file:
        expected_rc = int(file.read())

    with open(f"{file_name}.src", "r") as file:
        src = file.read()

    directory, file_name = file_name.split("/")[-2:]
     
    test = Test(directory, file_name,
                expected_output, expected_rc,
                program.stdout, program.stderr, program.returncode,
                src, num_test)

    return test


def test_dir(dirname: str) -> None:
    path = os.path.join(dirname, "*.src")
    files = list(map(lambda x: x.replace(".src", ""), list(glob.glob(path))))
    print(f"{BLUE} Runninng tests for {dirname} {BLACK}")
    for num_test, file in enumerate(files):
        test = run_program(file, num_test + 1)
        test.check_if_passed()
        test_dic[test.dirname].append(test)
        test.print_test()

num_files = {}
for folder in glob.glob("./interpret_tests/*"):
    num_files[folder.split('/')[-1]] = len(list(glob.glob(os.path.join(folder, "*.src"))))

for folder in glob.glob("./interpret_tests/*"):
    test_dir(folder)

total = passed = 0

for test_dir in test_dic.keys():
    for test in test_dic[test_dir]:
        passed += test.passed and test.return_code_passed
        total += 1


# passed = sum(test.passed for test in test_dic[test_dir] for test_dir in test_dic.keys())
# total = sum(1 for test in test_dic[test_dir] for test_dir in test_dic.keys())

print(f"{YELLOW} Passed {passed}/{total} tests.{BLACK}")
