import sys
import ast
import importlib.abc
import importlib.util
import time
import math
import random

class SmileyBool:
    def __init__(self, value):
        self._value = bool(value)

    def __eq__(self, other):
        return isinstance(other, SmileyBool) and self._value == other._value

    def __bool__(self):
        return self._value

    def __str__(self):
        return "True" if self._value else "False"

    def __repr__(self):
        return str(self)

__smileytrue__ = SmileyBool(True)
__smileyfalse__ = SmileyBool(False)

class SmileyNoneType:
    def __eq__(self, other):
        return isinstance(other, SmileyNoneType)

    def __bool__(self):
        return False

    def __str__(self):
        return "None"

    def __repr__(self):
        return "None"

__smileynone__ = SmileyNoneType()

class FixAddTransformer(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Add):
            return ast.BinOp(
                left=ast.Call(func=ast.Name(id='str', ctx=ast.Load()), args=[node.left], keywords=[]),
                op=ast.Add(),
                right=ast.Call(func=ast.Name(id='str', ctx=ast.Load()), args=[node.right], keywords=[]),
            )
        return node

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        if not any(isinstance(stmt, ast.Return) for stmt in node.body):
            if node.body:
                last_stmt = node.body[-1]
                if (
                    isinstance(last_stmt, ast.Expr) and
                    isinstance(last_stmt.value, ast.Call) and
                    isinstance(last_stmt.value.func, ast.Name) and
                    last_stmt.value.func.id == 'print' and
                    len(last_stmt.value.args) == 1
                ):
                    print_arg = last_stmt.value.args[0]
                    node.body[-1] = ast.Return(value=print_arg)
        return node

    def visit_NameConstant(self, node):
        if node.value is True:
            return ast.Name(id='__smileytrue__', ctx=ast.Load())
        elif node.value is False:
            return ast.Name(id='__smileyfalse__', ctx=ast.Load())
        elif node.value is None:
            return ast.Name(id='__smileynone__', ctx=ast.Load())
        return node

def read_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"Something went wrong: {e}")
        return None

def write_file(filename, content):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"File '{filename}' saved.")
    except Exception as e:
        print(f"Something went wrong while writing: {e}")

def _is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class SmileyfixLoader(importlib.abc.Loader):
    def __init__(self, fullname, path):
        self.fullname = fullname
        self.path = path

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        with open(self.path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=self.path)
        tree = FixAddTransformer().visit(tree)
        ast.fix_missing_locations(tree)
        code = compile(tree, filename=self.path, mode='exec')
        module.__dict__['time'] = time
        module.__dict__['math'] = math
        module.__dict__['random'] = random
        module.__dict__['read_file'] = read_file
        module.__dict__['write_file'] = write_file
        module.__dict__['__smileytrue__'] = __smileytrue__
        module.__dict__['__smileyfalse__'] = __smileyfalse__
        module.__dict__['__smileynone__'] = __smileynone__
        exec(code, module.__dict__)

class SmileyfixFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if path is None:
            path = ['']
        for entry in path:
            try:
                filename = f"{entry}/{fullname.replace('.', '/')}.py"
                with open(filename):
                    loader = SmileyfixLoader(fullname, filename)
                    return importlib.util.spec_from_file_location(fullname, filename, loader=loader)
            except FileNotFoundError:
                continue
        return None

def install_hook():
    sys.meta_path.insert(0, SmileyfixFinder())
    original_input = __builtins__.input
    def custom_input(prompt=""):
        user_input = original_input(prompt).strip()
        if user_input.isdigit():
            return int(user_input)
        elif _is_float(user_input):
            return float(user_input)
        else:
            return user_input
    __builtins__.input = custom_input

install_hook()
