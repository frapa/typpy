import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Type

import pytest

from typy import resolver
from typy.resolver import Resolver


@pytest.fixture
def resolver_case_dir(cases_dir: Path) -> Path:
    return cases_dir / "resolver"


@dataclass
class ResolverTestCase:
    case_id: str
    path: Path
    qualified_name: str
    containing_path: Path


@pytest.mark.parametrize(
    "case",
    [
        ResolverTestCase(
            case_id="standalone",
            path=Path("outer.py"),
            qualified_name="outer",
            containing_path=Path(),
        ),
        ResolverTestCase(
            case_id="standalone_subfolder",
            path=Path("scripts/inner.py"),
            qualified_name="inner",
            containing_path=Path("scripts"),
        ),
        ResolverTestCase(
            case_id="package_module",
            path=Path("pkg/mod.py"),
            qualified_name="pkg.mod",
            containing_path=Path(),
        ),
        ResolverTestCase(
            case_id="subpackage_module",
            path=Path("pkg/subpkg/submod.py"),
            qualified_name="pkg.subpkg.submod",
            containing_path=Path(),
        ),
        ResolverTestCase(
            case_id="package_init",
            path=Path("pkg/__init__.py"),
            qualified_name="pkg.__init__",
            containing_path=Path(),
        ),
        ResolverTestCase(
            case_id="package",
            path=Path("pkg"),
            qualified_name="pkg",
            containing_path=Path(),
        ),
        ResolverTestCase(
            case_id="subpackage",
            path=Path("pkg/subpkg"),
            qualified_name="pkg.subpkg",
            containing_path=Path(),
        ),
    ],
    ids=lambda case: case.case_id,
)
def test_resolver(
    resolver_case_dir: Path,
    case: ResolverTestCase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    file_path = resolver_case_dir.joinpath(case.path)
    qualified_name, containing_path = Resolver().resolve(file_path)
    assert qualified_name == case.qualified_name
    assert containing_path == resolver_case_dir.joinpath(case.containing_path)

    # Try to import file
    monkeypatch.syspath_prepend(containing_path)
    importlib.import_module(qualified_name)


@dataclass
class ResolverErrorTestCase:
    case_id: str
    path: Path
    error: Type[Exception]


@pytest.mark.parametrize(
    "case",
    [
        ResolverErrorTestCase(
            case_id="not_a_package",
            path=Path("empty"),
            error=AssertionError,
        ),
        ResolverErrorTestCase(
            case_id="not_a_python_file",
            path=Path("config.yml"),
            error=AssertionError,
        ),
        ResolverErrorTestCase(
            case_id="not_a_python_file_subfolder",
            path=Path("pkg/py.typed"),
            error=AssertionError,
        ),
    ],
    ids=lambda case: case.case_id,
)
def test_resolver_errors(resolver_case_dir: Path, case: ResolverErrorTestCase) -> None:
    file_path = resolver_case_dir.joinpath(case.path)
    with pytest.raises(case.error):
        Resolver().resolve(file_path)


class Counter:
    def __init__(self):
        self.count = 0

    def reset_count(self) -> None:
        self.count = 0

    def increment(self) -> None:
        self.count += 1


@pytest.fixture
def system_calls(monkeypatch: pytest.MonkeyPatch) -> Counter:
    counter = Counter()

    original_is_dir = Path.is_dir

    def is_dir(*args):
        print("is_dir()", *args)
        counter.increment()
        return original_is_dir(*args)

    original_exists = Path.exists

    def exists(*args):
        print("exists()", *args)
        counter.increment()
        return original_exists(*args)

    monkeypatch.setattr(resolver.Path, "is_dir", is_dir)
    monkeypatch.setattr(resolver.Path, "exists", exists)

    return counter


def test_caching(resolver_case_dir: Path, system_calls: Counter) -> None:
    """Test that the package caching works."""
    resolver = Resolver()
    assert system_calls.count == 0

    resolver.resolve(resolver_case_dir / "pkg" / "subpkg" / "submod.py")
    assert system_calls.count == 3

    system_calls.reset_count()
    resolver.resolve(resolver_case_dir / "pkg" / "subpkg" / "submod2.py")
    assert system_calls.count == 0
