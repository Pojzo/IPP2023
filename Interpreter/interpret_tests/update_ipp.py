import glob
import os
from lxml import etree


TEST_DIR = "./interpret_tests"

folders = list(glob.glob(os.path.join(TEST_DIR, "*")))

for folder in folders:
    for file in glob.glob(os.path.join(folder, "*.src")):
        with open(file, "r") as f:
            content = f.read()
            content = content.replace("IPPcode21", "IPPcode23")
            print(content)

        with open(file, "w") as f:
            f.write(content)
