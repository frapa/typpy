from typing import Type


def fmt_type(_type: Type) -> str:
    if _type is None:
        return "None"

    # This if for objects from the typing module,
    # such as Optional or Union
    if hasattr(_type, "_name"):
        return str(_type).replace("typing.", "")

    if "<class" in str(_type):
        return _type.__name__

    return str(_type)
