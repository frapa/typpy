from dataclasses import dataclass
from typing import Type, Any

import pytest

from typy.expression import get_expr_type
from typy.scope import Scope, parse_scope
from ..utils import ast_parse_expr


def add(a: int, b: int) -> int:
    return a + b


@pytest.fixture
def scope(namespace: Any) -> Scope:
    namespace.add = add

    return parse_scope(namespace)


@dataclass(frozen=True)
class GetExprTypeTestCase:
    case_id: str
    code: str
    type: Type


@pytest.mark.parametrize(
    "case",
    [
        GetExprTypeTestCase(case_id="literal_int", code="1", type=int),
        GetExprTypeTestCase(case_id="literal_float", code="1.0", type=float),
        GetExprTypeTestCase(case_id="literal_complex", code="2j", type=complex),
        GetExprTypeTestCase(case_id="literal_bool", code="True", type=bool),
        GetExprTypeTestCase(case_id="literal_str", code="'string'", type=str),
        GetExprTypeTestCase(case_id="literal_bytes", code="b'bytes'", type=bytes),
        GetExprTypeTestCase(case_id="call", code="add(1, 2)", type=int),
    ],
    ids=lambda case: case.case_id,
)
def test_get_expr_type(scope: Scope, case: GetExprTypeTestCase) -> None:
    expr = ast_parse_expr(case.code)
    _type = get_expr_type(expr, scope)
    assert _type == case.type
