from dataclasses import dataclass
from typing import Type, Any, Union, Tuple, List, Dict, Set

import pytest

from typpy.expression import get_expr_type
from typpy.scope import Scope, parse_scope
from ..utils import ast_parse_expr


def add(a: int, b: int) -> int:
    return a + b


@pytest.fixture
def scope(namespace: Any) -> Scope:
    namespace.Union = Union
    namespace.Tuple = Tuple
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
        GetExprTypeTestCase(
            case_id="literal_tuple", code="(1, '2')", type=Tuple[int, str]
        ),
        GetExprTypeTestCase(case_id="list_empty", code="[]", type=List),
        GetExprTypeTestCase(case_id="list_func", code="list()", type=List),
        GetExprTypeTestCase(case_id="list_uniform", code="[1, 2]", type=List[int]),
        GetExprTypeTestCase(
            case_id="list_union", code="[1, '2']", type=List[Union[int, str]]
        ),
        GetExprTypeTestCase(case_id="dict_empty", code="{}", type=Dict),
        GetExprTypeTestCase(case_id="dict_func", code="dict()", type=Dict),
        GetExprTypeTestCase(
            case_id="dict_uniform", code="{'a': 1, 'b': 2}", type=Dict[str, int]
        ),
        GetExprTypeTestCase(
            case_id="dict_typed",
            code="{'a': 1, 'b': [1]}",
            type=Dict[str, Union[int, List[int]]],
        ),
        GetExprTypeTestCase(case_id="set_empty", code="set()", type=Set),
        GetExprTypeTestCase(case_id="set_uniform", code="{1, 2, 3}", type=Set[int]),
        GetExprTypeTestCase(
            case_id="set_union", code="{1, '2', 3.0}", type=Set[Union[int, str, float]]
        ),
        GetExprTypeTestCase(
            case_id="subscript_type_union", code="Union[int, str]", type=Union[int, str]
        ),
        GetExprTypeTestCase(
            case_id="subscript_type_tuple", code="Tuple[int, str]", type=Tuple[int, str]
        ),
        GetExprTypeTestCase(case_id="call", code="add(1, 2)", type=int),
    ],
    ids=lambda case: case.case_id,
)
def test_get_expr_type(scope: Scope, case: GetExprTypeTestCase) -> None:
    expr = ast_parse_expr(case.code)
    _type = get_expr_type(expr, scope)
    assert _type == case.type
