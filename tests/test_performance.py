from pathlib import Path

import pytest


from typpy import run


@pytest.mark.xfail
def test_performance(cases_dir: Path) -> None:
    """Run typpy on the source code of a large library (SQLAlchemy)
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
    run(["typpy", str(cases_dir / "sqlalchemy" / "./**/*.py")])
