from pathlib import Path

import pytest

@pytest.fixture
def test_dir() -> Path:
    return Path(__file__).parent

@pytest.fixture
def cases_dir(test_dir: Path) -> Path:
    return test_dir / "cases"
