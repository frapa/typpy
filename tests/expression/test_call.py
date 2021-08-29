from typing import Any, Tuple, Union
from dataclasses import dataclass

import pytest

from typpy.scope import Scope, parse_scope
from typpy.expression.call import check_call
from ..utils import ast_parse_call, CheckTestCase, parametrize_case


def add(a: int, b: int) -> int:
    return a + b


def add_tuple(t: Tuple[int, int]) -> int:
    return t[0] + t[1]


def add_union(a: Union[int, str], b: Union[int, str]) -> str:
    return f"{a} + {b}"


def add_default(a: int, b: int = 1) -> int:
    return a + b


def add_to_str(s: str, num: int) -> str:
    return f"{s} + {num}"


@pytest.fixture
def scope(namespace: Any) -> Scope:
    namespace.add = add
    namespace.add_default = add_default
    namespace.add_tuple = add_tuple
    namespace.add_union = add_union
    namespace.add_to_str = add_to_str

    scope = parse_scope(namespace)

    scope.add_variable("var1", int)
    scope.add_variable("var2", float)

    return scope


@dataclass(frozen=True)
class CheckCallTestCase(CheckTestCase):
    ...


@parametrize_case(
    # Function or argument that does not exist
    CheckCallTestCase(
        case_id="does_not_exist",
        code="does_not_exist(1, 2)",
        errors=["Function 'does_not_exist' is not defined"],
    ),
    CheckCallTestCase(
        case_id="keyword_does_not_exist",
        code="add(1, 2, c=3)",
        errors=["Unexpected argument 'c' in call to 'add'"],
    ),
    # Too many, too few, duplicated args
    CheckCallTestCase(
        case_id="positional_missing",
        code="add(1)",
        errors=["Missing argument 'b' in call to 'add'"],
    ),
    CheckCallTestCase(
        case_id="positional_missing_multiple",
        code="add()",
        errors=["Missing arguments 'a', 'b' in call to 'add'"],
    ),
    CheckCallTestCase(
        case_id="positional_too_many",
        code="add(1, 2, 3)",
        errors=["Expected 2 arguments in call to 'add', found 3"],
    ),
    CheckCallTestCase(
        case_id="keyword_too_many",
        code="add(a=1, b=2, c=3)",
        errors=["Unexpected argument 'c' in call to 'add'"],
    ),
    CheckCallTestCase(
        case_id="duplicate",
        code="add(1, 2, a=1)",
        errors=["Got multiple values for argument 'a' to 'add'"],
    ),
    # This also tests that multiple errors can be reported
    CheckCallTestCase(
        case_id="duplicate_and_type_error",
        code="add(1, None, a=1, b=2.0)",
        errors=[
            "Expected 'int' as argument 'b' to 'add', found 'NoneType'",
            "Got multiple values for argument 'a' to 'add'",
            "Got multiple values for argument 'b' to 'add'",
            "Expected 'int' as argument 'b' to 'add', found 'float'",
        ],
    ),
    # Positional
    CheckCallTestCase(case_id="positional", code="add(1, 2)"),
    CheckCallTestCase(
        case_id="positional_error",
        code="add(1, 2.0)",
        errors=["Expected 'int' as argument 'b' to 'add', found 'float'"],
    ),
    CheckCallTestCase(case_id="positional_variable", code="add(var1, 2)"),
    CheckCallTestCase(
        case_id="positional_variable_error",
        code="add(1, var2)",
        errors=["Expected 'int' as argument 'b' to 'add', found 'float'"],
    ),
    CheckCallTestCase(case_id="positional_tuple", code="add_tuple((1, 2))"),
    CheckCallTestCase(
        case_id="positional_tuple_error",
        code="add_tuple((1, '2'))",
        errors=[
            "Expected 'Tuple[int, int]' as argument 't' to 'add_tuple', found 'Tuple[int, str]'"
        ],
    ),
    CheckCallTestCase(case_id="positional_union", code="add_union(1, '2')"),
    CheckCallTestCase(
        case_id="positional_union_error",
        code="add_union('1', 2.0)",
        errors=[
            "Expected 'Union[int, str]' as argument 'b' to 'add_union', found 'float'"
        ],
    ),
    # Keyword & Mixed
    CheckCallTestCase(case_id="keyword_constants", code="add_to_str(s='1', num=2)"),
    CheckCallTestCase(
        case_id="keyword_constants_error",
        code="add_to_str(s='1', num='2')",
        errors=["Expected 'int' as argument 'num' to 'add_to_str', found 'str'"],
    ),
    CheckCallTestCase(case_id="mixed_constants", code="add_to_str('1', num=2)"),
)
def test_check_call(scope: Scope, case: CheckCallTestCase) -> None:
    expr = ast_parse_call(case.code)
    errors = check_call(expr, scope)
    assert [err.message for err in errors] == case.errors
