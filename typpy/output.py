import sys
from typing import List

from colorama import Fore, Style

from typpy.error import TypingError


# TODO: tests
def print_errors(errors: List[TypingError], print_context: bool = True) -> None:
    last_file = None

    num_files = 0
    for error in errors:
        if error.file != last_file:
            print(f"{Style.BRIGHT}{error.file}{Style.RESET_ALL}", file=sys.stderr)
            last_file = error.file
            num_files += 1

        print(
            (
                f"  {error.file}:{error.line_number}: "
                f"{Style.BRIGHT}{error.message}{Style.RESET_ALL}"
            ),
            file=sys.stderr,
        )
        if print_context:
            # TODO: cache text
            content = error.file.read_text().split("\n")
            snippet = content[error.line_number - 1]

            if error.end_column_number is None:
                cursor_char = "^"
                length = 1
            else:
                cursor_char = "~"
                length = error.end_column_number - error.column_number

            str_line_number = str(error.line_number)
            line_number_offset = " " * len(str_line_number)
            cursor = (
                " " * error.column_number
                + cursor_char * length
                + f" {error.code_message}"
            )

            print(
                f"\n"
                f"    {line_number_offset}|\n"
                f"    {str_line_number}| {snippet}\n"
                f"    {line_number_offset}| "
                f"{Style.BRIGHT}{Fore.RED}{cursor}{Style.RESET_ALL}\n"
            )

    print()
    print(f"Found {len(errors)} errors in {num_files} files")
