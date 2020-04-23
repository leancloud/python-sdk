# coding: utf-8
import ast
import os
import re
import tempfile

# this script should be excuted under python_SDK/tests
def main():
    file_list = [
        f
        for f in os.listdir(".")
        if re.search("^test_.*\.py$", f) and f != ("test_mypy.py" or "test_engine.py")
    ]
    temp_dir = tempfile.gettempdir()

    for f in file_list:
        f_buf = open(f)
        f_text = f_buf.read()
        f_buf.close()
        file_name = "mypy_" + f

        nodes = ast.walk(ast.parse(f_text))
        tests = [
            node.name
            for node in nodes
            if type(node) == ast.FunctionDef and node.name.startswith("test")
        ]

        test_file = temp_dir + "/" + file_name
        mypy_test = open(test_file, "w")
        mypy_test.write("import {}\n\n".format(f[:-3]))
        middle = "()\n" + f[:-3] + "."
        funcs = middle.join(tests)
        funcs += "()"
        funcs = f[:-3] + "." + funcs
        mypy_test.write(funcs)
        mypy_test.close()
        os.system("mypy {}".format(test_file))
        os.remove(test_file)


if __name__ == "__main__":
    main()
