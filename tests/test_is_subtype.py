from dataclasses import dataclass
from typing import Type, Tuple, Optional, Union, Any

import pytest

from typpy.is_subtype import is_subtype
from tests.utils import if_py


def type_name(_type: Optional[Type]) -> str:
    if _type is None:
        return "None"

    # This if for objects from the typing module,
    # such as Optional or Union
    if hasattr(_type, "_name"):
        return str(_type).replace("typing.", "")

    if "<class" in str(_type):
        return _type.__name__

    return str(_type)


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
        IsSubtypeTestCase(Tuple[int, float], Any, True),
        IsSubtypeTestCase(Any, Any, True),
        # Tuples
        IsSubtypeTestCase(Tuple[int, float], Tuple[int, float], True),
        *if_py(
            ">=3.9", "IsSubtypeTestCase(tuple[int, float], Tuple[int, float], True)"
        ),
        IsSubtypeTestCase(Tuple[int, float], Tuple[float, float], True),
        IsSubtypeTestCase(Tuple[int, str], Tuple[int, float], False),
        IsSubtypeTestCase(Tuple[int, str], int, False),
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
    ids=lambda case: f"{type_name(case.actual)}-{type_name(case.expected)}-{case.result}",
)
def test_is_subtype(case: IsSubtypeTestCase):
    assert is_subtype(case.actual, case.expected) == case.result
