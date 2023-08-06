# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import unicode_literals

import io
import os.path
import sys

import setuptools


MODULE_NAME = "pytablewriter"
REPOSITORY_URL = "https://github.com/thombashi/{:s}".format(MODULE_NAME)
REQUIREMENT_DIR = "requirements"
ENCODING = "utf8"

pkg_info = {}


def pytest_runner_requires():
    if set(["pytest", "test", "ptr"]).intersection(sys.argv):
        return ["pytest-runner"]

    return []


def get_release_command_class():
    try:
        from releasecmd import ReleaseCommand
    except ImportError:
        return {}

    return {"release": ReleaseCommand}


with open(os.path.join(MODULE_NAME, "__version__.py")) as f:
    exec(f.read(), pkg_info)

with io.open("README.rst", encoding=ENCODING) as f:
    long_description = f.read()

with io.open(os.path.join("docs", "pages", "introduction", "summary.txt"), encoding=ENCODING) as f:
    summary = f.read().strip()

with open(os.path.join(REQUIREMENT_DIR, "requirements.txt")) as f:
    install_requires = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "test_requirements.txt")) as f:
    tests_requires = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "docs_requirements.txt")) as f:
    docs_requires = [line.strip() for line in f if line.strip()]

setuptools_require = ["setuptools>=38.3.0"]

excel_requires = ["xlwt", "XlsxWriter>=0.9.6,<2.0.0"]
es7_requires = ["elasticsearch>=7.0.5,<8"]
from_requires = ["pytablereader>=0.26.4,<2"]
html_requires = ["dominate>=2.1.5,<3.0.0"]
logging_requires = ["Logbook>=0.12.3,<2.0.0"]
sqlite_requires = ["SimpleSQLite>=0.45.3,<2"]
toml_requires = ["toml>=0.9.3,<1.0.0"]
optional_requires = ["simplejson>=3.8.1,<4.0"]
all_requires = (
    excel_requires
    + es7_requires
    + from_requires
    + html_requires
    + logging_requires
    + sqlite_requires
    + toml_requires
    + optional_requires
)
tests_requires = frozenset(tests_requires + all_requires)

setuptools.setup(
    name=MODULE_NAME,
    version=pkg_info["__version__"],
    url=REPOSITORY_URL,
    author=pkg_info["__author__"],
    author_email=pkg_info["__email__"],
    description=summary,
    include_package_data=True,
    keywords=[
        "table",
        "CSV",
        "Excel",
        "JavaScript",
        "JSON",
        "LTSV",
        "Markdown",
        "MediaWiki",
        "HTML",
        "pandas",
        "reStructuredText",
        "SQLite",
        "TSV",
        "TOML",
    ],
    license=pkg_info["__license__"],
    long_description=long_description,
    long_description_content_type="text/x-rst",
    packages=setuptools.find_packages(exclude=["test*"]),
    project_urls={
        "Documentation": "https://{:s}.rtfd.io/".format(MODULE_NAME),
        "Source": REPOSITORY_URL,
        "Tracker": "{:s}/issues".format(REPOSITORY_URL),
    },
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=setuptools_require + install_requires,
    setup_requires=setuptools_require + pytest_runner_requires(),
    tests_require=tests_requires,
    extras_require={
        "all": all_requires,
        "dev": ["releasecmd>=0.2.0,<1", "twine", "wheel"],
        "docs": docs_requires,
        "excel": excel_requires,
        "es5": ["elasticsearch>=5.5.3,<6"],
        "es6": ["elasticsearch>=6.3.1,<7"],
        "es7": es7_requires,
        "html": html_requires,
        "from": from_requires,
        "logging": logging_requires,
        "sqlite": sqlite_requires,
        "test": tests_requires,
        "toml": toml_requires,
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: LaTeX",
    ],
    cmdclass=get_release_command_class(),
)
