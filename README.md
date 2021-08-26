# Typpy - Python Type Checker

![example workflow](https://github.com/frapa/typpy/actions/workflows/main.yml/badge.svg)

Typpy is an experimental type checker for Python. It's similar to mypy,
but instead of statically checking the code, it dynamically imports the
modules and is therefore able to perform type check that mypy is unable
to perform. This particularly includes decorated classes and functions.

## Requirements

Typpy support Python 3.6 and newer. It does not have dependencies outside
the standard library.

## Quick Start

```bash
typpy path/to/file.py
```

## Status

Currently, typpy is still in a very early stage and only support a limited
number of type checks. 
