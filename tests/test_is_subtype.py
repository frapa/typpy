from __future__ import annotations

from dataclasses import dataclass
from typing import Type, Optional, Union, Any

import pytest

from typpy.is_subtype import is_subtype
from typpy.format import fmt_type
from tests.utils import if_py


@dataclass(frozen=True)
class IsSubtypeTestCase:
    actual: Optional[Type]
    expected: Optional[Type]
    result: bool


@pytest.mark.parametrize(
    "case",
    [
        IsSubtypeTestCase(int, int, True),
        IsSubtypeTestCase(float, str, False),
        IsSubtypeTestCase(str, int, False),
        # Numeric types are a bit of a mess in python
        # for instance issubclass(int, float) == False,
        # but type checkers are required to accept
        # ints where floats are accepted by PEP 484.
        # This function takes the pragmatic approach
        # of accepting ints in place of floats.
        # The same is true for complex numbers.
        IsSubtypeTestCase(int, float, True),
        IsSubtypeTestCase(int, complex, True),
        IsSubtypeTestCase(float, complex, True),
        # bool is a subclass of int
        # (the mess above is not enough!)
        IsSubtypeTestCase(bool, int, True),
        IsSubtypeTestCase(bool, float, True),
        IsSubtypeTestCase(bool, complex, True),
        # None means type(None) and should be accepted
        IsSubtypeTestCase(None, None, True),
        # Any should always return True
        IsSubtypeTestCase(None, Any, True),
        IsSubtypeTestCase(int, Any, True),
        IsSubtypeTestCase(tuple[int, float], Any, True),
        IsSubtypeTestCase(Any, Any, True),
        # Tuples
        IsSubtypeTestCase(tuple[int, float], tuple[int, float], True),
        *if_py(
            ">=3.9", "IsSubtypeTestCase(tuple[int, float], tuple[int, float], True)"
        ),
        IsSubtypeTestCase(tuple[int, float], tuple[float, float], True),
        IsSubtypeTestCase(tuple[int, str], tuple[int, float], False),
        IsSubtypeTestCase(tuple[int, str], int, False),
        # Union types
        IsSubtypeTestCase(Optional[int], Optional[int], True),
        IsSubtypeTestCase(None, Optional[int], True),
        IsSubtypeTestCase(int, Optional[int], True),
        IsSubtypeTestCase(Optional[int], int, False),
        IsSubtypeTestCase(int, Union[int, float, bytes], True),
        IsSubtypeTestCase(str, Union[int, float, bytes], False),
        IsSubtypeTestCase(Union[float, bytes], Union[int, float, bytes], True),
        IsSubtypeTestCase(Union[str, bytes], Union[int, float, bytes], False),
        IsSubtypeTestCase(Union[str, bytes], int, False),
        # Since is a subclass if float, it should be accepted
        IsSubtypeTestCase(bool, Union[float, bytes], True),
    ],
    ids=lambda case: f"{fmt_type(case.actual)}-{fmt_type(case.expected)}-{case.result}",
)
def test_is_subtype(case: IsSubtypeTestCase):
    assert is_subtype(case.actual, case.expected) == case.result
