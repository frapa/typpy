import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from typpy.scope import Scope


@dataclass(frozen=True)
class TypingError:
    file: Path
    line_number: int
    column_number: int
    end_column_number: Optional[int]
    message: str
    code_message: str = ""

    @classmethod
    def from_scope_stmt(
        cls,
        scope: Scope,
        tree: Union[ast.AST, ast.keyword],
        message: str,
        code_message: str = "",
    ) -> "TypingError":
        if isinstance(tree, ast.keyword):
            line_number = tree.value.lineno
            # -1 for the equal sign. We assume no whitespace,
            # if there is some whitespace the worst that happens
            # is that the underline will be a little off
            length = len(tree.arg)
            column_number = tree.value.col_offset - 1 - length
            end_column_number = getattr(tree.value, "end_col_offset", None)
        else:
            line_number = tree.lineno
            column_number = tree.col_offset
            end_column_number = getattr(tree, "end_col_offset", None)

        return cls(
            file=scope.file,
            line_number=line_number,
            column_number=column_number,
            end_column_number=end_column_number,
            message=message,
            code_message=code_message,
        )
