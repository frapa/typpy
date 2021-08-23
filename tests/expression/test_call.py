from typing import Any, List
from dataclasses import dataclass, field

import pytest

from typpy.scope import Scope, parse_scope
from typpy.expression import check_call
from typpy.error import TypingError
from ..utils import ast_parse_call


def add(a: int, b: int) -> int:
    return a + b


@pytest.fixture
def scope(namespace: Any) -> Scope:
    namespace.add = add
    namespace.var1 = 1

    return parse_scope(namespace)


@dataclass(frozen=True)
class CheckCallTestCase:
    case_id: str
    code: str
    errors: List[TypingError] = field(default_factory=list)


@pytest.mark.parametrize(
    "case",
    [
        CheckCallTestCase(case_id="positional", code="add(1, 2)"),
        CheckCallTestCase(case_id="keyword_constants", code="add(a=1, b=2)"),
    ],
    ids=lambda case: case.case_id,
)
def test_check_call(scope: Scope, case: CheckCallTestCase) -> None:
    expr = ast_parse_call(case.code)
    errors = check_call(expr, scope)
    assert errors == []
