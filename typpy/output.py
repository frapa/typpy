import sys
from typing import List

from typpy.error import TypingError


# TODO: tests
def print_errors(errors: List[TypingError]) -> None:
    last_file = None

    for error in errors:
        if error.file != last_file:
            print(error.file, file=sys.stderr)
            last_file = error.file

        print(f"  line {error.line_number}: {error.message}", file=sys.stderr)
