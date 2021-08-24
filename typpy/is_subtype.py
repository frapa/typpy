from typing import Type, Union, Tuple


# TODO: test
def is_subtype(act_type: Type, exp_type: Type) -> bool:
    origin_type = getattr(exp_type, "__origin__", None)
    if origin_type is not None:
        if origin_type == Union:
            return _check_union(act_type, exp_type)
        # elif origin_type == tuple:
        #     return _check_tuple(act_type, exp_type)
    else:
        return issubclass(act_type, exp_type)

    raise NotImplementedError(f"is_subtype() for type {exp_type} is not implemented")


def _check_union(act_type: Type, exp_type: Type) -> bool:
    for union_type in exp_type.__args__:
        if is_subtype(act_type, union_type):
            return True

    return False


# def _check_tuple(act_type: Type, exp_type: Type) -> bool:
#     print(888)
#     for tuple_type in exp_type.__args__:
#         print("-->", tuple_type)
#
#     return False
