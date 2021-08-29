# Typpy - Python Type Checker

![example workflow](https://github.com/frapa/typpy/actions/workflows/main.yml/badge.svg)

Typpy is an experimental type checker for Python. It's similar to mypy,
but instead of statically checking the code, it dynamically imports the
modules and is therefore able to perform type check that mypy is unable
to perform. This particularly includes decorated classes and functions.

## Goals

Why another python type checker? 

 - Check most python source files, even if not explicitly
   annotated. Try to extract typing information if not available.
 - Strict mode by default. Ensure your code is typed, but do not require
   dependencies to be typed. Our philosophy is that each line of code
   that is not type checked can contain a bug or error.
 - Support gradual typing as an option.
 - Support dynamic python constructs such as decorators. We make
   heavy use of them and annotating them right is a pain. Typpy tries
   to check typing even without decorator annotations.
 - Provide great error messages.

## Requirements

Typpy support Python 3.7 and newer.

## Quick Start

```bash
typpy path/to/file.py
```

## Status

Currently, typpy is still in a very early stage and only support a limited
number of type checks:

 - Variable assignments
 - Function calls

Typpy right now even crashes on certain source code inputs. I'm adding support
for different python constructs such as comparison expressions, classes, import
statements and so on. I expect typpy to be able to check most real world code
in the next few weeks.

## Python version support

Python's `typing` module and the specs are rapidly evolving with each python
minor version. Therefore, it costs a lot of time to maintain and implement
support for many python versions.

Since python 3.6 has end-of-life in December 2021, typpy does not support it. 
I encourage developers to upgrade python to a supported version.
