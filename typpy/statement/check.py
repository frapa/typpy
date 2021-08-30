import ast
import logging
import warnings
from typing import List

from typpy.error import TypingError
from typpy.expression import check_expression
from typpy.scope import Scope
from typpy.statement.assignment import check_assignment


def check_statement(stmt: ast.stmt, scope: Scope) -> List[TypingError]:
    logging.debug("stmt: %s" % stmt)

    # These two are already evaluated by the module import
    # and are retrieved dynamically instead of parsed.
    if isinstance(stmt, (ast.ClassDef, ast.FunctionDef)):
        return []

    errors = []
    if isinstance(stmt, ast.If):
        errors = check_expression(stmt.test, scope)
    elif isinstance(stmt, (ast.Assign, ast.AnnAssign)):
        errors = check_assignment(stmt, scope)
    elif isinstance(stmt, ast.Expr):
        errors = check_expression(stmt.value, scope)
    else:
        warnings.warn(
            f"check for statement {stmt} is not implemented. Contact us for a fix."
        )

    for sub_stmt in getattr(stmt, "body", []):
        new_errors = check_statement(sub_stmt, scope)
        errors.extend(new_errors)

    return errors
