import ast
import inspect
import sys
import types
from contextlib import contextmanager
from importlib import import_module
from pathlib import Path
from typing import Iterable, Generator, Any, Callable, Optional, Type

from typy.expression import check_call
from typy.resolver import Resolver
from typy.scope import Scope


# TODO: clen-up/remove this class
class FileModule:
    def __init__(self, name: str, path: Path, module: types.ModuleType):
        self.name = name
        self.path = path
        self.module = module


# TODO: docstring
class TypeChecker:
    def __init__(self):
        self.resolver = Resolver()

    def check_files(self, files: Iterable[Path]) -> None:
        pending_files = set(files)
        processed_files = set()

        while pending_files:
            file = pending_files.pop()
            self._check_file(file)
            processed_files.add(file)

    @contextmanager
    def import_module(self, path: Path) -> Generator[FileModule, None, None]:
        module_name, containing_path = self.resolver.resolve(path)

        sys.path.append(str(containing_path))
        module = import_module(module_name)

        yield FileModule(module_name, path, module)

        sys.path.remove(str(containing_path))

    def _check_file(self, path: Path) -> None:
        with self.import_module(path) as module:
            self._check_scope(module.module)

    def _check_scope(
        self,
        obj: Any,
        parent_scope: Optional[Scope] = None,
    ) -> None:
        # Parse scope before everything else so that all symbols
        # are already parsed and can be referenced without assuming
        # they come before the checked statement.
        scope = self._parse_scope(obj, parent_scope)
        tree = ast.parse(inspect.getsource(obj))

        for stmt in tree.body:
            self._check_statement(stmt)

        # Check sub-scopes
        for cb in scope.callables.values():
            self._check_scope(cb[0], scope)

        print()
        print(obj, scope)

    def _parse_scope(
        self,
        container: Any,
        parent_scope: Optional[Scope] = None,
    ) -> Scope:
        """Populate scope with all existing symbols."""
        scope = Scope(parent_scope)

        for symbol, obj in container.__dict__.items():
            if isinstance(obj, Callable):
                signature = inspect.signature(obj)
                scope.add_callable(f"{obj.__module__}.{obj.__name__}", obj, signature)

            if isinstance(obj, Type):
                print(2, obj)

        return scope

    def _check_statement(self, stmt: ast.stmt, scope: Scope) -> None:
        # These two are already evaluated by the module import
        # and are retrieved dynamically instead of parsed.
        if isinstance(stmt, (ast.ClassDef, ast.FunctionDef)):
            return

        print("stmt", stmt)
        if isinstance(stmt, ast.If):
            self._check_expression(stmt.test, scope)
        elif isinstance(stmt, ast.Assign):
            self._check_expression(stmt.value, scope)
        elif isinstance(stmt, ast.Expr):
            self._check_expression(stmt.value, scope)

        for sub_stmt in getattr(stmt, "body", []):
            self._check_statement(sub_stmt, scope)

    def _check_expression(self, expr: ast.expr, scope: Scope) -> None:
        print("expr", expr)
        if isinstance(expr, ast.Compare):
            print(expr.left, expr.comparators, expr.ops)
        elif isinstance(expr, ast.Call):
            print(expr.func.id, expr.args)
            check_call(expr, scope)
