# Typpy - Python Type Checker

![example workflow](https://github.com/frapa/typpy/actions/workflows/main.yml/badge.svg)

Typpy is an experimental type checker for Python. It's similar to mypy,
but instead of statically checking the code, it dynamically imports the
modules and is therefore able to perform type check that mypy is unable
to perform. This particularly includes decorated classes and functions.

## Requirements

Typpy support Python 3.7 and newer. It does not have dependencies outside
the standard library.

## Quick Start

```bash
typpy path/to/file.py
```

## Status

Currently, typpy is still in a very early stage and only support a limited
number of type checks. 

## Python version support

Python's `typing` module and the specs are rapidly evolving with each python
minor version. Therefore, it costs a lot of time to maintain and implement
support for many python versions.

Since python 3.6 has end-of-life in December 2021, typpy does not support it. 
We encourage developers to upgrade python to a supported version.
