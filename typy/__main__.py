import logging
import os
import sys
from typing import List

from typy.discover_files import find_files
from typy.output import print_errors
from typy.type_checker import TypeChecker


# TODO: test, docstring
def run(args: List[str]) -> None:
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
