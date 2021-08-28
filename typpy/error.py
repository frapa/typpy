import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from typpy.scope import Scope


@dataclass(frozen=True)
class TypingError:
    file: Path
    line_number: int
    column_number: int
    end_column_number: Optional[int]
    message: str

    @classmethod
    def from_scope_stmt(
        cls,
        scope: Scope,
        stmt: ast.stmt,
        message: str,
    ) -> "TypingError":
        return cls(
            file=scope.file,
            line_number=stmt.lineno,
            column_number=stmt.col_offset,
            end_column_number=getattr(stmt, "end_col_offset", None),
            message=message,
        )
