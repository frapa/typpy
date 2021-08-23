from glob import glob
from pathlib import Path
from typing import List, Iterable


# TODO: test, docstring
def find_files(glob_patterns: List[str]) -> Iterable[Path]:
    for glob_pattern in glob_patterns:
        yield from _expand_glob(glob_pattern)


def _expand_glob(glob_pattern: str) -> Iterable[Path]:
    yield from (Path(path) for path in glob(glob_pattern))
