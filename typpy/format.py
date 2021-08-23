from typing import Type


def fmt_type(_type: Type) -> str:
    name = getattr(_type, "__name__", None)
    return name
