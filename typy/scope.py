import inspect
from typing import Any, Optional, Callable, Type, Dict


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

    def resolve_callable(self, name: str) -> Optional[inspect.Signature]:
        _, cb = self.callables.get(name, (None, None))

        if cb is None and self.parent is not None:
            return self.parent.resolve_callable(name)

        return cb

    def __str__(self) -> str:
        if self.variables:
            variables = "\n    " + ",\n    ".join(self.variables.keys()) + "\n  "
        else:
            variables = ""

        if self.callables:
            callables = "\n    " + ",\n    ".join(self.callables.keys()) + "\n  "
        else:
            callables = ""

        return (
            f"<Scope '{self.qualified_name}'\n"
            f"  variable=[{variables}]\n"
            f"  types=[]\n"
            f"  callables=[{callables}]\n"
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
        if isinstance(obj, Callable) and hasattr(obj, "__name__"):
            signature = inspect.signature(obj)
            scope.add_callable(obj.__name__, obj, signature)

    return scope
