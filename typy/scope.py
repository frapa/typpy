import inspect
from typing import Any, Optional


class Scope:
    def __init__(self, parent: "Optional[Scope]" = None):
        self.parent = parent
        # self.qualified_name =
        self.variables = {}
        self.callables = {}
        self.types = {}

    def add_callable(self, name: str, obj: Any, cb: inspect.Signature):
        self.callables[name] = (obj, cb)

    def __str__(self):
        if self.callables:
            callables = "\n    " + ",\n    ".join(self.callables.keys()) + "\n  "
        else:
            callables = ""

        return (
            f"<Scope\n"
            f"  variable=[]\n"
            f"  types=[]\n"
            f"  callables=[{callables}]\n"
            f">"
        )
