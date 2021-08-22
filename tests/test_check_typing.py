from pathlib import Path

from typy.type_checker import TypeChecker


def test_check_typing(cases_dir: Path) -> None:
    TypeChecker().check_files([cases_dir / "function" / "function.py"])
