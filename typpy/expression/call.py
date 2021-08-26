# flake8: noqa

import ast
import inspect
from typing import List, Type
from dataclasses import dataclass

from typpy.scope import Scope
from typpy.error import TypingError


@dataclass(frozen=True)
class Arg:
    name: str
    annotation: Type

    @classmethod
    def from_signature(cls, sign_arg: inspect.Parameter) -> "Arg":
        return cls(name=sign_arg.name, annotation=sign_arg.annotation)

    # @classmethod
    # def from_ast_args(cls, call_arg: ast.A) -> "Arg":
    #     return cls(name=sign_arg.name, annotation=sign_arg.annotation)


def check_call(expr: ast.Call, scope: Scope) -> List[TypingError]:
    _, signature = scope.resolve_callable(expr.func.id)
    if signature is None:
        # TODO: error reporting
        pass

    return _check_call_args(signature, expr)


def _check_call_args(signature: inspect.Signature, expr: ast.Call) -> List[TypingError]:
    errors = []

    sign_args = [sig_arg for sig_arg in signature.parameters.values()]
    required = [
        sign_arg
        for sign_arg in signature.parameters.values()
        if sign_arg.default == inspect._empty
    ]

    # First process all keyword arguments
    # for keyword in expr.keywords:
    #     value = keyword.value
    #     print(keyword.value.value, keyword.value.kind)
    #     # _check_arg(Arg(), Arg(keyword.arg, keyword.value.))
    #
    #     if keyword.arg in required:
    #         required.remove(keyword.arg)

    for call_arg in expr.args:
        sign_arg = sign_args.pop(0)
        print(sign_arg, call_arg)

    # print(arg.name, arg.kind, arg.default, arg.annotation)
    #
    # if arg.default == arg.empty:
    # Check that this required argument is passed
    # print(1111, expr.args, expr.keywords)

    return errors


def _check_arg(sig_arg: Arg, call_arg: Arg) -> TypingError:
    pass
