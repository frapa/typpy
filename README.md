# Typy - Python Type Checker

Typy is an experimental type checker for Python. It's similar to mypy,
but instead of statically checking the code, it dynamically imports the
modules and is therefore able to perform type check that mypy is unable
to perform. This particularly includes decorated classes and functions.

## Requirements

Typy support Python 3.6 and newer. It does not have dependencies outside
the standard library.

## Quick Start

```bash
typy path/to/file.py
```
