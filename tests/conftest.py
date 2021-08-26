from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def test_dir() -> Path:
    return Path(__file__).parent


@pytest.fixture
def cases_dir(test_dir: Path) -> Path:
    return test_dir / "cases"


@pytest.fixture
def namespace() -> Any:
    class Namespace:
        __name__ = "namespace"

        def __getattr__(self, attr: str) -> Any:
            return self.__dict__[attr]

        def __setattr__(self, attr: str, value: Any) -> None:
            self.__dict__[attr] = value

    return Namespace()
