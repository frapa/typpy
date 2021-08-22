import ast
import logging
from typing import List

# from typy.expression.call import check_call
from typy.error import TypingError
from typy.scope import Scope


def check_expression(expr: ast.expr, scope: Scope) -> List[TypingError]:
    logging.debug("expr: %s" % expr)
    errors = []

    if isinstance(expr, ast.Compare):
        print(expr.left, expr.comparators, expr.ops)
    # elif isinstance(expr, ast.Call):
    #     new_errors = check_call(expr, scope)
    #     errors.extend(new_errors)

    return errors
