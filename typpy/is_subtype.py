from typing import Type, Union, Tuple, Any, Optional
from inspect import isclass


# TODO: test
def is_subtype(act_type: Optional[Type], exp_type: Optional[Type]) -> bool:
    act_type = type(None) if act_type is None else act_type
    exp_type = type(None) if exp_type is None else exp_type

    # optimization for common use case
    if act_type is exp_type:
        return True

    # SPECIAL CASES
    # =============
    # if the expected type is Any, the result is always True
    if exp_type is Any:
        return True
    # For numeric types, we follow PEP 484, and not
    # the class hierarchy (e.g. issubclass(int, float)
    # is False but we return True)
    elif exp_type is float and act_type in (int, bool):
        return True
    elif exp_type is complex and act_type in (float, int, bool):
        return True

    exp_origin_type = getattr(exp_type, "__origin__", None)
    if exp_origin_type is not None:
        # This if for objects from the typing module,
        # such as Optional or Union
        if exp_origin_type is Union:
            return _check_union(act_type, exp_type)
        elif exp_origin_type in (Tuple, tuple):
            return _check_tuple(act_type, exp_type)
    elif isclass(act_type):
        return issubclass(act_type, exp_type)
    else:
        # This happens when act_type is a Tuple or Union
        # and ext_type is not. This is always False.
        return False

    raise NotImplementedError(f"is_subtype() for type {exp_type} is not implemented")


def _check_union(act_type: Type, exp_type: Union) -> bool:
    # If the act_type is an Union, check that act_type is a subset
    if getattr(act_type, "__origin__", None) is Union:
        union_types = set(exp_type.__args__)
        return all(t in union_types for t in act_type.__args__)

    # Otherwise, check it act_type is contained in the Union
    for union_type in exp_type.__args__:
        if is_subtype(act_type, union_type):
            return True

    return False


def _check_tuple(act_type: Type, exp_type: Tuple) -> bool:
    if getattr(act_type, "__origin__", None) in (tuple, Tuple):
        return all(
            is_subtype(act, exp)
            for act, exp in zip(act_type.__args__, exp_type.__args__)
        )

    return False
