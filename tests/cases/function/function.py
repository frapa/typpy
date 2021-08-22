# This one is also callable, but is not a function.
# typy should ignore this when
class ExampleClass:
    ...


def add(a: int, b: int) -> int:
    return a + b


def sub(a, b):
    return a - b


if __name__ == "__main__":
    s = add("a", "b")
    sub(1, "b")
