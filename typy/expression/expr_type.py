import ast
from typing import Type

from typy.scope import Scope


def get_expr_type(expr: ast.expr, scope: Scope) -> Type:
    if isinstance(expr, ast.Constant):
        return type(expr.value)
    elif isinstance(expr, ast.Call):
        signature = scope.resolve_callable(expr.func.id)
        if signature is None:
            # TODO: error reporting
            pass

        return signature.return_annotation

    raise NotImplementedError(f"expression type for {expr} was not yet implemented")
