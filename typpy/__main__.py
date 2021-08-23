import logging
import os
import sys
from typing import List

from typpy.discover_files import find_files
from typpy.output import print_errors
from typpy.type_checker import TypeChecker


# TODO: test, docstring
def run(args: List[str] = None) -> None:
    args = args or sys.argv

    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper())

    # TODO: move to proper function
    files = find_files([args[1]])

    type_checker = TypeChecker()
    errors = type_checker.check_files(files)

    if errors:
        print_errors(errors)
        sys.exit(1)


if __name__ == "__main__":
    run(sys.argv)
