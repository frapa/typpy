import ast
from typing import List, Union, Type

from typpy.error import TypingError
from typpy.expression import check_expression, get_expr_type
from typpy.format import fmt_type
from typpy.scope import Scope
from typpy.is_subtype import is_subtype


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
            if annotation is not None and not is_subtype(_type, annotation):
                return [
                    _assignment_error(target.id, _type, annotation, stmt.value, scope)
                ]

            scope.add_variable(target.id, _type)
        elif isinstance(target, ast.Tuple):
            _type = get_expr_type(stmt.value, scope)
            for elt, elt_type in zip(target.elts, _type.__args__):
                annotation = scope.resolve_variable(elt.id)
                if annotation is not None and not is_subtype(_type, annotation):
                    return [
                        _assignment_error(
                            elt.id, elt_type, annotation, stmt.value, scope
                        )
                    ]

                scope.add_variable(elt.id, elt_type)
        else:
            raise NotImplementedError(
                f"assignment for target {target} is not implemented. "
                f"Contact us for a fix."
            )

    return []


def _check_annotated_assignment(stmt: ast.AnnAssign, scope: Scope) -> List[TypingError]:
    if not isinstance(stmt.target, ast.Name):
        raise NotImplementedError(
            f"assignment for target {stmt.target} is not implemented. "
            f"Contact us for a fix."
        )

    annotation = get_expr_type(stmt.annotation, scope)
    _type = get_expr_type(stmt.value, scope)
    if not is_subtype(_type, annotation):
        return [_assignment_error(stmt.target.id, _type, annotation, stmt.value, scope)]

    scope.add_variable(stmt.target.id, _type)

    return []


def _assignment_error(
    var_name: str,
    act_type: Type,
    exp_type: Type,
    stmt: Union[ast.Assign, ast.AnnAssign],
    scope: Scope,
) -> TypingError:
    message = (
        f"Expected '{fmt_type(exp_type)}' in assignment to '{var_name}', "
        f"found '{fmt_type(act_type)}'"
    )
    code_message = f"Expected '{fmt_type(exp_type)}', found '{fmt_type(act_type)}'"
    return TypingError.from_scope_stmt(scope, stmt, message, code_message)
