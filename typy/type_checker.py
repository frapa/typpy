import ast
import inspect
import logging
import sys
import types
from contextlib import contextmanager
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Iterable, Generator, Any

from typy.expression import check_expression
from typy.resolver import Resolver
from typy.scope import Scope, parse_scope
from typy.statement import check_assignment


@dataclass(frozen=True)
class FileModule:
    qualified_name: str
    path: Path
    module: types.ModuleType


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
        try:
            module = import_module(module_name)

            yield FileModule(
                qualified_name=module_name,
                path=path,
                module=module,
            )
        finally:
            sys.path.remove(str(containing_path))

    def _check_file(self, path: Path) -> None:
        with self.import_module(path) as module:
            scope = parse_scope(module.module)
            # Bootstrap scope qualified name
            scope.qualified_name = module.qualified_name
            self._check_scope_typing(module.module, scope)

    def _check_scope(
        self,
        obj: Any,
        parent_scope: Scope,
    ) -> None:
        # Parse scope before everything else so that all symbols
        # are already parsed and can be referenced without assuming
        # they come before the checked statement.
        scope = parse_scope(obj, parent_scope)
        self._check_scope_typing(obj, scope)

    def _check_scope_typing(self, obj: Any, scope: Scope) -> None:
        tree = ast.parse(inspect.getsource(obj))

        for stmt in tree.body:
            self._check_statement(stmt, scope)

        # Check sub-scopes
        for cb in scope.callables.values():
            self._check_scope(cb[0], scope)

        logging.debug("obj: %s - scope: %s" % (obj.__name__, scope))

    def _check_statement(self, stmt: ast.stmt, scope: Scope) -> None:
        logging.debug("stmt: %s" % stmt)

        # These two are already evaluated by the module import
        # and are retrieved dynamically instead of parsed.
        if isinstance(stmt, (ast.ClassDef, ast.FunctionDef)):
            return

        if isinstance(stmt, ast.If):
            check_expression(stmt.test, scope)
        elif isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            check_assignment(stmt, scope)
        elif isinstance(stmt, ast.Expr):
            check_expression(stmt.value, scope)
        for sub_stmt in getattr(stmt, "body", []):
            self._check_statement(sub_stmt, scope)
