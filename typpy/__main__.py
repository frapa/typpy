import os
import sys
import logging
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import List
from dataclasses import dataclass

from typpy.discover_files import find_files
from typpy.output import print_errors
from typpy.type_checker import TypeChecker
from typpy.error import TypingError


# TODO: test, docstring
def run(args: List[str] = None) -> None:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper())

    args = args or sys.argv
    options = _parse_args(args[1:])

    files = list(find_files(options.patterns))
    type_checker = TypeChecker()
    errors = type_checker.check_files(files)

    if errors:
        print_errors(errors, print_context=options.print_context)
        sys.exit(1)

    print(f"No issues found in {len(files)} files")


@dataclass(frozen=True)
class Options:
    patterns: List[str]
    print_context: bool


def _parse_args(args: List[str]) -> Options:
    parser = ArgumentParser(
        prog="typpy",
        description=(
            "Type check python source files.\n\n"
            "Pass in a list of wildcard patterns matching \n"
            "the source files that you want to type check:\n\n"
            "$ typpy src/**/*.py tests/**/*.py"
        ),
        formatter_class=RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "patterns",
        metavar="PATTERN",
        nargs="+",
        help=(
            "Wildcard pattern matching source files to type check. "
            "Can contain '*' to indicate any character sequence, "
            "and '**' to indicate any folder structure. "
            "Multiple patterns can be passed in."
        ),
    )
    parser.add_argument(
        "--no-context",
        action="store_true",
        help=(
            "Do not print error context (showing where the error "
            "occurred in the code). "
        ),
    )

    ns = parser.parse_args(args)
    return Options(
        patterns=ns.patterns,
        print_context=not ns.no_context,
    )


def type_check(patterns: List[str]) -> List[TypingError]:
    files = find_files(patterns)

    type_checker = TypeChecker()
    errors = type_checker.check_files(files)

    return errors


if __name__ == "__main__":
    run(sys.argv)
