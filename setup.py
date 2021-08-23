# Necessary to build wheel
import setuptools
from distutils.core import setup
from pathlib import Path

ROOT = Path(__file__).parent

setup(
    name="typy",
    version="0.0.0",
    description="Python Static Type Checker",
    long_description=(ROOT / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Francesco Pasa",
    author_email="francescopasa@gmail.com",
    url="https://github.com/frapa/typy",
    license="GPL3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Typing :: Typed",
    ],
    packages=["typy"],
    package_data={
        "typy": ["py.typed"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": ["typy=typy.__main__:run"],
    },
)
