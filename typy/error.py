from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TypingError:
    file: Path
    line_number: int
    column_number: int
    message: str
