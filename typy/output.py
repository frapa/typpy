import sys
from typing import List

from typy.error import TypingError


# TODO: tests
def print_errors(errors: List[TypingError]) -> None:
    for error in errors:
        print(error.message, file=sys.stderr)
