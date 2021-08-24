import ast
from typing import Type, Tuple

from typpy.scope import Scope


def get_expr_type(expr: ast.expr, scope: Scope) -> Type:
    if isinstance(expr, ast.Constant):
        return type(expr.value)
    elif isinstance(expr, ast.Name):
        return eval(expr.id)
    elif isinstance(expr, ast.Subscript):
        outer_type, _ = scope.resolve_callable(expr.value.id)

        # The outer type annotation can contain a single type
        # or a tuple of types
        if isinstance(expr.slice, ast.Tuple):
            inner_type = tuple(get_expr_type(elt, scope) for elt in expr.slice.elts)
        else:
            inner_type = get_expr_type(expr.slice, scope)

        return outer_type[inner_type]
    elif isinstance(expr, ast.Call):
        _, signature = scope.resolve_callable(expr.func.id)
        if signature is None:
            # TODO: error reporting
            pass

        return signature.return_annotation
    elif isinstance(expr, ast.Tuple):
        types = [get_expr_type(elt, scope) for elt in expr.elts]
        return Tuple[tuple(types)]

    raise NotImplementedError(f"expression type for {expr} is not implemented")
