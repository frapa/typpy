from __future__ import annotations

import inspect
from typing import Any, Optional, Type
import warnings
from functools import lru_cache


@lru_cache(maxsize=None)
def get_builtin_scope() -> "Scope":
    class BuiltinContainer:
        def __init__(self):
            self.__dict__ = __builtins__
            self.__name__ = "BuiltinContainer"

    return parse_scope(BuiltinContainer())


class Scope:
    def __init__(
        self,
        name: str,
        parent: "Optional[Scope]" = None,
    ):
        self.name = name
        self.parent = parent

        self.file = None
        self.qualified_name = None
        if parent is None:
            # Avoid recursion
            if name != "BuiltinContainer":
                self.parent = get_builtin_scope()
        else:
            self.file = parent.file
            self.qualified_name = f"{parent.qualified_name}.{name}"

        self.variables: dict[str, Type] = {}
        self.types = {}
        self.callables = {}

    def add_variable(self, name: str, annotation: Type) -> None:
        self.variables[name] = annotation

    def resolve_variable(self, name: str) -> Optional[Type]:
        annotation = self.variables.get(name, None)
        if annotation is None and self.parent is not None:
            annotation = self.parent.resolve_variable(name)

        return annotation

    def add_callable(self, name: str, obj: Any, cb: inspect.Signature) -> None:
        self.callables[name] = (obj, cb)

    def resolve_callable(self, name: str) -> Optional[tuple[Any, inspect.Signature]]:
        obj, cb = self.callables.get(name, (None, None))

        if cb is None and self.parent is not None:
            return self.parent.resolve_callable(name)

        return obj, cb

    @staticmethod
    def _format_dict(dictionary: dict[str, Any]) -> str:
        if dictionary:
            items = ",\n    ".join(dictionary.keys())
            return f"\n    {items}\n  "

        return ""

    def __str__(self) -> str:
        return (
            f"<Scope '{self.qualified_name}'\n"
            f"  variable=[{self._format_dict(self.variables)}]\n"
            f"  types=[]\n"
            f"  callables=[{self._format_dict(self.callables)}]\n"
            f">"
        )


# TODO: tests
def parse_scope(
    container: Any,
    parent_scope: Optional[Scope] = None,
) -> Scope:
    """Populate scope with all existing symbols."""
    scope = Scope(container.__name__, parent_scope)

    objects = dict(container.__dict__)
    for symbol, obj in objects.items():
        if callable(obj):
            try:
                signature = inspect.signature(obj)
            except ValueError:
                # This happens for certain builtin magic stuff
                warnings.warn(f"inspect.signature does not work for {obj}")
                continue

            scope.add_callable(symbol, obj, signature)

    return scope
