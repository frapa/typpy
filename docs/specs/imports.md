# Typy and imports

This spec defines how typy handles importing files
and resolves imports.

## Background

Typy takes as input a list of files to type check. Even when
the input is defined with wildcard patterns, typy internally
generates a list of files to type check.

To effectively check a file, typy must know the signatures
of imported symbols, and thus must be able to resolve imports.

## Definitions

 - *package* - A directory containing a `__init__.py` file.
 - *subpackage* -  A package contained inside another package.
 - *parent package* - The container package of a subpackage.
 - *standalone import* - When a file is imported as `import <file>`
   even when part of a package. This requires `sys.path` to contain 
   the file parent folder.

## Scenarios

### Check package files

A common scenario is checking files in a package or subpackage. 
For instance, imagine the following file structure:

```text
my_project/
  my_package/
    my_subpackage/
      __init__.py
      subpackage_file1.py
      subpackage_file2.py
      ...
      
    __init__.py
    package_file1.py
    package_file2.py
    package_other_file.ext
    ...
      
  file1.py
  other_file1.ext1
  other_file2.ext2
  ...
```

Then imagine that typy is instructed to type check all python
files in the package (e.g. `my_package/**/*.py`).

In this scenario, files would import other files from the same package,
subpackages or the parent packages in one of the following ways:

- `from <package>.<file> import <symbol>` (or equivalent syntax).
  In this case, the folder containing the package (i.e. `my_project`)
  must be added to path. Note that this folder might not be the
  current working directory where typy has been invoked. This
  would work even if the file is imported standalone.
- `from .<file> import <symbol>` (or equivalent syntax).
  This case is similar to the one above, but the file must be
  imported by typy using the package syntax and not standalone.
- `from my_subpackage.<file> import <symbol>` (or equivalent syntax).
  Same remark as above.
- `from ..<file> import <symbol>` (or equivalent syntax).
  Same remark as above, but file must be imported with full
  package path and `sys.path` cannot just contain the subpackage
  parent folder.

With *equivalent syntax* we mean other import statements such as
`import <package>.<file>.<symbol>` instead of 
`from <package>.<file> import <symbol>`, which are equivalent
but syntactically different.

### Check standalone scripts and modules

This is another common scenario. It happens when we want to check a
standalone script folder such as:

```text
scripts/
  file1.py
  file2.py
  other_file.ext
```

In this case, the python files `file1.py` and `file2.py` are
standalone scripts or modules. They can be imported standalone,
and can contain imports of type `from <another_file> import <symbol>`
(or equivalent).

This case is easy, as just setting the `sys.path` to the file
parent folder is sufficient to correctly resolve imports.

### Check project

Another common scenario similar to the package scenario happens
when the whole project folder is set to be checked (e.g. `./**/*.py`).

The difference with the case above is that also `file1.py` has to be
type checked. This file can be simply checked as a standalone script
or module as in the scenario above.

Thus `typy` needs to be able to mix and match both import types.

### Import of external packages

Imagine having a script containing the following code:

```python
from requests import get

def get_books() -> List[Book]:
    books = get("http://api.my_service.my_app.com/v1/books").json
    ...
```

In this case, typy must be able to resolve `requests.get`.
For this to happen, typy must be run in an environment
(e.g. a virtualenv) where the `requests` library is installed.

All external imports are resolved as package imports.

## Specification

Typy should generate a list of files to type check.
For each file (e.g. `pkg/subpkg/file.py`), typy will
try to determine a fully qualified name (e.g. `pkg.subpkg.file`).
The directory containing the package is then added to
the search path.

For the case of standalone scripts, the fully qualified
name is simply the file name, so the import algorithm works 
also in that case.

Typy should evaluate the modules using the python interpreter
to be able to resolve dynamic situations such as decorators
adding methods to classes.

Typy should automatically filter only `.py` files from the 
list of files that have been passed as input. This avoids
trying to resolve non-python files.

### Efficiency

Reading and resolving large amounts of files can be time-consuming,
especially in environments with slow I/O or on laptops with antivirus
software. Typy should avoid hitting the filesystem whenever possible.

When checking files in a package, it often happens that the same package
folder has to be resolved again and again. Typy should cache the package
folders to avoid too many system calls.

### Problems

*Note:* For these it is necessary to have test cases.

#### Accidental ambiguous import

This might happen when we have a folder like this

```text
folder/
  scripts/
    script.py
    json.py
```

and `script.py` contains the following code:

```python
import json

...
```

Assuming that typy has been called from `folder`,
adding the script parent folder (e.g. `scripts`) to `sys.path`
will cause the import to become ambiguous (we cannot determine
anymore if we want to import `json.py` or the standard library
`json` module).

This does not only affect typy but also simply running
`python script.py` form the `script` folder will be ambiguous.

In this case, typy should behave like the python interpreter.

#### Modules

Since type evaluates the modules it checks, if the modules contain
instructions on the global scope. These instructions will be
executed. For instance, a script containing

```python
import shutil

shutil.rmtree("my_dir")
```

cannot be safely executed by typy, without as a side effect deleting
`my_dir` and its content. This is different from other type chekers
such as mypy. In such cases, we suggest that the authors wrap their
scripts in a `if __name__ == "__main__":` guard.
