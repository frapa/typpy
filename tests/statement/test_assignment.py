from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Dict, Type

import pytest

from typy.error import TypingError
from typy.scope import Scope, parse_scope
from typy.statement import check_assignment
from ..utils import ast_parse_assignment, CheckTestCase, parametrize_case


@pytest.fixture
def scope(namespace: Any) -> Scope:
    namespace.Optional = Optional

    return parse_scope(namespace)


@dataclass(frozen=True)
class CheckAssignmentTestCase(CheckTestCase):
    variables: Dict[str, Type] = field(default_factory=dict)


@parametrize_case(
    CheckAssignmentTestCase(
        case_id="constant_assignment",
        code="var = 1",
        variables=dict(var=int),
    ),
    CheckAssignmentTestCase(
        case_id="double_constant_assignment",
        code="var1 = var2 = 1",
        variables=dict(var1=int, var2=int),
    ),
    CheckAssignmentTestCase(
        case_id="destructuring_assignment",
        code="var1, var2 = (1, 2.0)",
        variables=dict(var1=int, var2=float),
    ),
    CheckAssignmentTestCase(
        case_id="annotated_constant_assignment",
        code="var: int = 1",
        variables=dict(var=int),
    ),
    CheckAssignmentTestCase(
        case_id="annotated_constant_assignment_none",
        code="var: Optional[int] = None",
        variables=dict(var=Optional[int]),
    ),
    CheckAssignmentTestCase(
        case_id="annotated_constant_assignment_error",
        code="var: int = 'string'",
        errors=[
            TypingError(
                file=Path(),
                line_number=1,
                column_number=0,
                message="Expected 'int' in assignment, found 'str'",
            )
        ],
    ),
)
def test_check_assignment(scope: Scope, case: CheckAssignmentTestCase) -> None:
    stmt = ast_parse_assignment(case.code)
    errors = check_assignment(stmt, scope)
    assert errors == case.errors

    # Check that new variables have been added to the scope
    for var, _type in case.variables.items():
        assert scope.variables[var] == _type
