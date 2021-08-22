from pathlib import Path

from typy import run


def test_performance(cases_dir: Path) -> None:
    """Run typy on the source code of a large library (SQLAlchemy)
    and see how it performs.

    SQLAlchemy summary:
    -------------------------------------------------------------------------------
    Language                     files          blank        comment           code
    -------------------------------------------------------------------------------
    Python                         233          36719          46206          95057
    C                                3            385            123           1759
    -------------------------------------------------------------------------------
    SUM:                           236          37104          46329          96816
    -------------------------------------------------------------------------------
    """
    run(["typy", str(cases_dir / "sqlalchemy" / "./**/*.py")])
