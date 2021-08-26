import inspect
from typing import Any, Optional, Type, Dict, Tuple


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
        if parent is not None:
            self.file = parent.file
            self.qualified_name = f"{parent.qualified_name}.{name}"

        self.variables: Dict[str, Type] = {}
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

    def resolve_callable(self, name: str) -> Optional[Tuple[Any, inspect.Signature]]:
        obj, cb = self.callables.get(name, (None, None))

        if cb is None and self.parent is not None:
            return self.parent.resolve_callable(name)

        return obj, cb

    @staticmethod
    def _format_dict(dictionary: Dict[str, Any]) -> str:
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

    for symbol, obj in container.__dict__.items():
        if callable(obj):
            signature = inspect.signature(obj)

            if hasattr(obj, "__name__"):
                name = obj.__name__
            # This if for objects from the typing module,
            # such as Optional or Union
            elif hasattr(obj, "_name"):
                name = obj._name
            else:
                raise NotImplementedError(
                    f"name retrieval for callable '{obj}' is not implemented"
                )

            scope.add_callable(name, obj, signature)

    return scope
