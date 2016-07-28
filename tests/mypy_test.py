import ast
import os

def main():
    file_list = [f for f in os.listdir('.') if f.endswith('.py') and f !='test_mypy.py']

    for f in (file_list[-10], ):
        f_buf = open(f)
        f_text = f_buf.read()
        f_buf.close()
        file_name = 'mypy_' + f

        nodes = ast.walk(ast.parse(f_text))
        tests = [node.name for node in nodes if type(node) == ast.FunctionDef and node.name.startswith('test')]

        mypy_test = open(file_name, 'w')
        mypy_test.write('import {}\n\n'.format(f[:-3]))
        middle = '()\n' + f[:-3] + '.' 
        funcs = middle.join(tests)
        funcs += '()'
        funcs = f[:-3] + '.' + funcs
        mypy_test.write(funcs)
        mypy_test.close()

        os.system('mypy {}'.format(file_name))
        # os.system('rm {}'.format(file_name))


if __name__ == '__main__':
    main()
