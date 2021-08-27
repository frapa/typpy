import sys
from typing import List

from typpy.error import TypingError


# TODO: tests
def print_errors(errors: List[TypingError]) -> None:
    last_file = None

    num_files = 0
    for error in errors:
        if error.file != last_file:
            print(error.file, file=sys.stderr)
            last_file = error.file
            num_files += 1

        print(f"  {error.file}:{error.line_number}: {error.message}", file=sys.stderr)

    print()
    print(f"Found {len(errors)} errors in {num_files} file")
