import sys
from typing import List

from typy.discover_files import find_files
from typy.type_checker import TypeChecker


# TODO: test, docstring
def run(args: List[str]) -> None:
    # TODO: move to proper function
    files = find_files([args[1]])

    type_checker = TypeChecker()
    type_checker.check_files(files)


if __name__ == "__main__":
    run(sys.argv)
