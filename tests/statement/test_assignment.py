from typing import Any, Optional

import pytest

from typy.scope import Scope, parse_scope
from typy.statement import check_assignment
from ..utils import ast_parse_assignment, CheckTestCase, parametrize_case


@pytest.fixture
def scope(namespace: Any) -> Scope:
    namespace.Optional = Optional

    return parse_scope(namespace)


@parametrize_case(
    CheckTestCase(case_id="constant_assignment", code="var = 1"),
    CheckTestCase(case_id="double_constant_assignment", code="var1 = var2 = 1"),
    CheckTestCase(case_id="destructuring_assignment", code="var1, var2 = (1, 2)"),
    CheckTestCase(case_id="annotated_constant_assignment", code="var: int = 1"),
    CheckTestCase(
        case_id="annotated_constant_assignment_none", code="var: Optional[int] = None"
    ),
    CheckTestCase(
        case_id="annotated_constant_assignment_error",
        code="var: int = 'string'",
        errors=[],
    ),
)
def test_check_assign(scope: Scope, case: CheckTestCase) -> None:
    stmt = ast_parse_assignment(case.code)
    errors = check_assignment(stmt, scope)
    assert errors == case.errors
