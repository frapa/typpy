import ast
from pathlib import Path
from typing import List, Union

from typy.error import TypingError
from typy.expression import check_expression, get_expr_type
from typy.format import fmt_type
from typy.scope import Scope


def check_assignment(
    stmt: Union[ast.Assign, ast.AnnAssign], scope: Scope
) -> List[TypingError]:
    errors = check_expression(stmt.value, scope)

    if isinstance(stmt, ast.Assign):
        new_errors = _check_plain_assignment(stmt, scope)
    else:
        new_errors = _check_annotated_assignment(stmt, scope)

    errors.extend(new_errors)

    print(stmt)

    return errors


def _check_plain_assignment(stmt: ast.Assign, scope: Scope) -> List[TypingError]:
    for target in stmt.targets:
        if isinstance(target, ast.Name):
            _type = get_expr_type(stmt.value, scope)
            scope.add_variable(target.id, _type)
        # elif isinstance(target, ast.Tuple):
        #     ...
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

    annotation = eval(stmt.annotation.id)
    _type = get_expr_type(stmt.value, scope)
    if annotation != _type:
        return [
            TypingError(
                file=Path(),
                line_number=0,
                column_number=0,
                message=(
                    f"Expected '{fmt_type(annotation)}' in assignment, "
                    f"found '{fmt_type(_type)}'"
                ),
            )
        ]

    scope.add_variable(stmt.target.id, _type)

    return []
