from __future__ import annotations

import ast
import warnings
from typing import Type, Union, Iterable, Any

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
        cb, signature = scope.resolve_callable(expr.func.id)
        if signature is None:
            # TODO: error reporting
            pass

        # The annotation can also be a string
        if isinstance(signature.return_annotation, str):
            return eval(signature.return_annotation)

        return signature.return_annotation
    elif isinstance(expr, ast.Tuple):
        types = [get_expr_type(elt, scope) for elt in expr.elts]
        return tuple[tuple(types)]
    elif isinstance(expr, ast.List):
        return _resolve_union(list, expr.elts, scope)
    elif isinstance(expr, ast.Dict):
        key_types = {get_expr_type(key, scope) for key in expr.keys}
        value_types = {get_expr_type(value, scope) for value in expr.values}

        if not key_types:
            return dict

        if len(key_types) == 1:
            key_type = key_types.pop()
        else:
            key_type = Union[tuple(key_types)]

        if len(value_types) == 1:
            value_type = value_types.pop()
        else:
            value_type = Union[tuple(value_types)]

        return dict[key_type, value_type]
    elif isinstance(expr, ast.Set):
        return _resolve_union(set, expr.elts, scope)

    warnings.warn(
        f"expression type for {expr} is not implemented. Contact us for a fix."
    )


def _resolve_union(parent: Type, values: Iterable[Any], scope: Scope) -> Type:
    types = {get_expr_type(value, scope) for value in values}

    if not types:
        return parent
    elif len(types) == 1:
        return parent[types.pop()]

    return parent[Union[tuple(types)]]
