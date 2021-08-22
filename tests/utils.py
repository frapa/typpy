import ast
from dataclasses import dataclass, field
from typing import List, TypeVar

import pytest

from typy.error import TypingError


def ast_parse_stmt(code: str) -> ast.stmt:
    stmt = ast.parse(code).body[0]
    return stmt


def ast_parse_assignment(code: str) -> ast.Assign:
    stmt = ast_parse_stmt(code)
    assert isinstance(stmt, (ast.Assign, ast.AnnAssign)), stmt
    return stmt


def ast_parse_expr(code: str) -> ast.expr:
    stmt = ast_parse_stmt(code)
    assert isinstance(stmt, ast.Expr), stmt
    return stmt.value


def ast_parse_call(code: str) -> ast.Call:
    expr = ast_parse_expr(code)
    assert isinstance(expr, ast.Call), expr
    return expr


@dataclass(frozen=True)
class CheckTestCase:
    case_id: str
    code: str
    errors: List[TypingError] = field(default_factory=list)


T = TypeVar("T")


def parametrize_case(*cases: CheckTestCase):
    def decorator(func: T) -> T:
        return pytest.mark.parametrize(
            "case",
            cases,
            ids=lambda case: case.case_id,
        )(func)

    return decorator
