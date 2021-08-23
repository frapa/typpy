import ast
from typing import Type, Tuple

from typpy.scope import Scope


def get_expr_type(expr: ast.expr, scope: Scope) -> Type:
    if isinstance(expr, ast.Constant):
        return type(expr.value)
    elif isinstance(expr, ast.Call):
        signature = scope.resolve_callable(expr.func.id)
        if signature is None:
            # TODO: error reporting
            pass

        return signature.return_annotation
    elif isinstance(expr, ast.Tuple):
        types = [get_expr_type(elt, scope) for elt in expr.elts]
        return Tuple[tuple(types)]

    raise NotImplementedError(f"expression type for {expr} is not implemented")
