import ast
from typing import Type, Tuple

from typpy.scope import Scope


def get_expr_type(expr: ast.expr, scope: Scope) -> Type:
    # In python 3.7, constants are NameConstant, Str, Bytes or Num
    # instead of being a single Constant class
    if isinstance(expr, (ast.Constant, ast.NameConstant)):
        return type(expr.value)
    elif isinstance(expr, (ast.Str, ast.Bytes)):
        return type(expr.s)
    elif isinstance(expr, ast.Num):
        return type(expr.n)
    elif isinstance(expr, ast.Name):
        val = scope.resolve_variable(expr.id)
        if val is None:
            return eval(expr.id)
        return val
    elif isinstance(expr, ast.Subscript):
        outer_type, _ = scope.resolve_callable(expr.value.id)

        # The outer type annotation can contain a single type
        # or a tuple of types
        if isinstance(expr.slice, ast.Tuple):
            inner_type = tuple(get_expr_type(elt, scope) for elt in expr.slice.elts)
        # On python up to 3.8, the inner part was a ast.Index
        # instead of an ast.Tuple
        elif isinstance(expr.slice, ast.Index):
            value = expr.slice.value
            # e.g. obj[1, 2, 3]
            if isinstance(value, ast.Tuple):
                inner_type = tuple(get_expr_type(elt, scope) for elt in value.elts)
            # e.g. obj[1]
            else:
                inner_type = get_expr_type(value, scope)
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
