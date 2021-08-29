import ast
import logging
import warnings
from typing import List

from typpy.expression.call import check_call
from typpy.error import TypingError
from typpy.scope import Scope


def check_expression(expr: ast.expr, scope: Scope) -> List[TypingError]:
    logging.debug("expr: %s" % expr)
    errors = []

    # if isinstance(expr, ast.Compare):
    #     print(expr.left, expr.comparators, expr.ops)
    if isinstance(expr, ast.Call):
        new_errors = check_call(expr, scope)
        errors.extend(new_errors)
    else:
        warnings.warn(f"check for expression {expr} is not implemented")

    return errors
