from functools import lru_cache
from pathlib import Path
from typing import Tuple


class Resolver:
    """Resolve paths into fully qualified module names,
    caching filesystem access for speed.
    """

    # Cache already resolved paths, to avoid hitting the
    # filesystem many times to resolve the same folders.
    @lru_cache(maxsize=None)
    def is_package(self, path: Path) -> bool:
        return (path / "__init__.py").exists()

    # See comment above
    @lru_cache(maxsize=None)
    def resolve(self, path: Path, _check_path: bool = True) -> Tuple[str, Path]:
        """Resolve paths into fully qualified module names.

        :param path: A path to a file or directory.
        :param _check_path: For internal use.
        :return: A tuple containing a fully qualified
            module name and the path to the folder containing
            the outermost package.
        """
        if _check_path:
            if path.suffix:
                # A file bust be a python source file
                assert path.suffix == ".py"

            # Check that the path is importable. If not, it should
            # not have been passed here to be resolved and indicates
            # a bug elsewhere.
            if path.suffix != ".py" and path.is_dir():
                # A directory should contain a __init__.py file
                assert self.is_package(path)

        if not self.is_package(path.parent):
            # We reached the folder containing the outermost package
            return path.stem, path.parent

        parent_qualified_name, containing_path = self.resolve(
            path.parent, _check_path=False
        )
        return f"{parent_qualified_name}.{path.stem}", containing_path
