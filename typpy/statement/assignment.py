import ast
from typing import List, Union

from typpy.error import TypingError
from typpy.expression import check_expression, get_expr_type
from typpy.format import fmt_type
from typpy.scope import Scope


def check_assignment(
    stmt: Union[ast.Assign, ast.AnnAssign], scope: Scope
) -> List[TypingError]:
    errors = check_expression(stmt.value, scope)

    if isinstance(stmt, ast.Assign):
        new_errors = _check_plain_assignment(stmt, scope)
    else:
        new_errors = _check_annotated_assignment(stmt, scope)

    errors.extend(new_errors)
    return errors


def _check_plain_assignment(stmt: ast.Assign, scope: Scope) -> List[TypingError]:
    for target in stmt.targets:
        if isinstance(target, ast.Name):
            annotation = scope.resolve_variable(target.id)
            _type = get_expr_type(stmt.value, scope)
            if annotation is not None and annotation != _type:
                message = (
                    f"Expected '{fmt_type(annotation)}' in assignment to '{target.id}', "
                    f"found '{fmt_type(_type)}'."
                )
                return [TypingError.from_scope_stmt(scope, stmt, message)]

            scope.add_variable(target.id, _type)
        elif isinstance(target, ast.Tuple):
            _type = get_expr_type(stmt.value, scope)
            for elt, elt_type in zip(target.elts, _type.__args__):
                annotation = scope.resolve_variable(elt.id)
                if annotation is not None and annotation != elt_type:
                    message = (
                        f"Expected '{fmt_type(annotation)}' in assignment to '{elt.id}', "
                        f"found '{fmt_type(elt_type)}'."
                    )
                    return [TypingError.from_scope_stmt(scope, stmt, message)]

                scope.add_variable(elt.id, elt_type)
        else:
            raise NotImplementedError(
                f"assignment for target {target} is not implemented"
            )

    return []


def _check_annotated_assignment(stmt: ast.AnnAssign, scope: Scope) -> List[TypingError]:
    if not isinstance(stmt.target, ast.Name):
        raise NotImplementedError(
            f"assignment for target {stmt.target} is not implemented"
        )

    assert isinstance(stmt.annotation, ast.Name), stmt
    annotation = eval(stmt.annotation.id)
    _type = get_expr_type(stmt.value, scope)
    if annotation != _type:
        message = (
            f"Expected '{fmt_type(annotation)}' in assignment to '{stmt.target.id}', "
            f"found '{fmt_type(_type)}'."
        )
        return [TypingError.from_scope_stmt(scope, stmt, message)]

    scope.add_variable(stmt.target.id, _type)

    return []
