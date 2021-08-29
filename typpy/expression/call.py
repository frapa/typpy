import ast
import inspect
from typing import List, Type

from typpy.scope import Scope
from typpy.error import TypingError
from typpy.is_subtype import is_subtype
from typpy.format import fmt_type
from typpy.expression.expr_type import get_expr_type


def check_call(expr: ast.Call, scope: Scope) -> List[TypingError]:
    cb, signature = scope.resolve_callable(expr.func.id)
    if signature is None:
        message = f"Function '{expr.func.id}' is not defined"
        return [TypingError.from_scope_stmt(scope, expr.func, message, message)]

    return _check_call_args(cb.__name__, signature, expr, scope)


def _check_call_args(
    cb_name: str,
    signature: inspect.Signature,
    expr: ast.Call,
    scope: Scope,
) -> List[TypingError]:
    errors = []

    sign_args = [sign_arg for sign_arg in signature.parameters.values()]
    required = [
        sign_arg
        for sign_arg in signature.parameters.values()
        if sign_arg.default == inspect._empty
    ]

    total_num_call_args = len(expr.args) + len(expr.keywords)
    # Positional arguments
    for call_arg in expr.args:
        # If this positional argument does not exist
        if not sign_args:
            message = (
                f"Expected {len(signature.parameters)} arguments "
                f"in call to '{expr.func.id}', found {total_num_call_args}"
            )
            code_message = (
                f"Expected {len(signature.parameters)} arguments, "
                f"found {total_num_call_args}"
            )
            errors.append(
                TypingError.from_scope_stmt(scope, call_arg, message, code_message)
            )
            continue

        sign_arg = sign_args.pop(0)

        call_arg_type = get_expr_type(call_arg, scope)
        if not is_subtype(call_arg_type, sign_arg.annotation):
            new_error = _argument_type_error(
                cb_name,
                call_arg_type,
                sign_arg,
                call_arg,
                scope,
            )
            errors.append(new_error)

        if sign_arg in required:
            required.remove(sign_arg)

    # First process all keyword arguments
    for keyword in expr.keywords:
        # If this keyword argument does not exist
        if keyword.arg not in signature.parameters:
            message = f"Unexpected argument '{keyword.arg}' in call to '{expr.func.id}'"
            code_message = f"Unexpected argument '{keyword.arg}'"
            errors.append(
                TypingError.from_scope_stmt(scope, keyword, message, code_message)
            )
            continue

        sign_arg = signature.parameters[keyword.arg]

        # Check that this argument was not already set by position
        if sign_arg not in sign_args:
            message = (
                f"Got multiple values for argument '{keyword.arg}'"
                f" to '{expr.func.id}'"
            )
            code_message = f"'{keyword.arg}' was already given"
            errors.append(
                TypingError.from_scope_stmt(scope, expr, message, code_message)
            )

        keyword_arg_type = get_expr_type(keyword.value, scope)
        if not is_subtype(keyword_arg_type, sign_arg.annotation):
            new_error = _argument_type_error(
                cb_name,
                keyword_arg_type,
                sign_arg,
                keyword,
                scope,
            )
            errors.append(new_error)

        if sign_arg in required:
            required.remove(sign_arg)

    # Check that all required arguments were removed
    if required:
        s = "" if len(required) == 1 else "s"
        args = ", ".join([f"'{arg.name}'" for arg in required])
        message = f"Missing argument{s} {args} in call to '{expr.func.id}'"
        code_message = f"Missing argument{s} {args}"
        errors.append(TypingError.from_scope_stmt(scope, expr, message, code_message))

    return errors


def _argument_type_error(
    cb_name: str,
    call_arg_type: Type,
    sign_arg: inspect.Parameter,
    expr: ast.expr,
    scope: Scope,
) -> TypingError:
    message = (
        f"Expected '{fmt_type(sign_arg.annotation)}' as argument '{sign_arg.name}' "
        f"to '{cb_name}', found '{fmt_type(call_arg_type)}'"
    )
    code_message = (
        f"Expected '{fmt_type(sign_arg.annotation)}', found '{fmt_type(call_arg_type)}'"
    )
    return TypingError.from_scope_stmt(scope, expr, message, code_message)
