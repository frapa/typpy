import ast

from typy.scope import Scope


def check_call(expr: ast.Call, scope: Scope) -> None:
    print(111)
