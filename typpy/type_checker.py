import ast
import inspect
import logging
import sys
import types
from contextlib import contextmanager
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Iterable, Generator, Any, List

from typpy.error import TypingError
from typpy.expression import check_expression
from typpy.resolver import Resolver
from typpy.scope import Scope, parse_scope
from typpy.statement import check_assignment


@dataclass(frozen=True)
class FileModule:
    qualified_name: str
    path: Path
    module: types.ModuleType


# TODO: docstring, tests
class TypeChecker:
    def __init__(self):
        self.resolver = Resolver()

    def check_files(self, files: Iterable[Path]) -> List[TypingError]:
        pending_files = set(files)
        processed_files = set()

        errors = []
        while pending_files:
            file = pending_files.pop()
            new_errors = self._check_file(file)
            errors.extend(new_errors)
            processed_files.add(file)

        return errors

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

    def _check_file(self, path: Path) -> List[TypingError]:
        with self.import_module(path) as module:
            scope = parse_scope(module.module)
            # TODO: better way to bootstrap?
            # Bootstrap scope qualified name
            scope.file = path
            scope.qualified_name = module.qualified_name
            return self._check_scope_typing(module.module, scope)

    def _check_scope(
        self,
        obj: Any,
        parent_scope: Scope,
    ) -> List[TypingError]:
        # Parse scope before everything else so that all symbols
        # are already parsed and can be referenced without assuming
        # they come before the checked statement.
        scope = parse_scope(obj, parent_scope)
        return self._check_scope_typing(obj, scope)

    def _check_scope_typing(self, obj: Any, scope: Scope) -> List[TypingError]:
        tree = ast.parse(inspect.getsource(obj))

        if not isinstance(obj, types.ModuleType):
            tree = tree.body[0]

        errors = []
        for stmt in tree.body:
            new_errors = self._check_statement(stmt, scope)
            errors.extend(new_errors)

        # Check sub-scopes
        # TODO: clean-up
        for cb in scope.callables.values():
            new_errors = self._check_scope(cb[0], scope)
            errors.extend(new_errors)

        logging.debug("obj: %s - scope: %s" % (obj.__name__, scope))

        return errors

    def _check_statement(self, stmt: ast.stmt, scope: Scope) -> List[TypingError]:
        logging.debug("stmt: %s" % stmt)

        # These two are already evaluated by the module import
        # and are retrieved dynamically instead of parsed.
        if isinstance(stmt, (ast.ClassDef, ast.FunctionDef)):
            return []

        errors = []
        if isinstance(stmt, ast.If):
            errors = check_expression(stmt.test, scope)
        elif isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            errors = check_assignment(stmt, scope)
        elif isinstance(stmt, ast.Expr):
            errors = check_expression(stmt.value, scope)

        for sub_stmt in getattr(stmt, "body", []):
            new_errors = self._check_statement(sub_stmt, scope)
            errors.extend(new_errors)

        return errors
