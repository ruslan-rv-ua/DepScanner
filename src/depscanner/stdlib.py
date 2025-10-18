"""Standard library detection utilities."""

import sys
from typing import TypeAlias

PythonVersion: TypeAlias = tuple[int, int]


def get_stdlib_modules(python_version: PythonVersion = (3, 10)) -> set[str]:
    """Return a set of standard library module names.

    Args:
        python_version: Python version tuple (major, minor).
                       Only used for documentation purposes.
                       Always returns current Python's stdlib.

    Returns:
        Set of standard library module names.

    Note:
        This function uses sys.stdlib_module_names (Python 3.10+)
        to get the list of stdlib modules for the currently running
        Python interpreter. The python_version parameter is kept
        for API compatibility but doesn't affect the result.
    """
    if hasattr(sys, "stdlib_module_names"):
        return set(sys.stdlib_module_names)

    # Fallback for Python < 3.10 (though we require 3.10+)
    return _get_fallback_stdlib_modules()


def is_stdlib(module_name: str, python_version: PythonVersion = (3, 10)) -> bool:
    """Check if a module is part of the standard library.

    Args:
        module_name: The module name to check (can be dotted, e.g., 'os.path').
        python_version: Python version tuple (kept for API compatibility).

    Returns:
        True if the module is part of the standard library.

    Examples:
        >>> is_stdlib('os')
        True
        >>> is_stdlib('os.path')
        True
        >>> is_stdlib('requests')
        False
    """
    # Get the top-level module name for dotted imports
    top_level = module_name.split(".")[0]

    stdlib_modules = get_stdlib_modules(python_version)
    return top_level in stdlib_modules


def generate_stdlib_list(python_version: PythonVersion = (3, 10)) -> set[str]:
    """Generate a list of standard library modules programmatically.

    This is an alias for get_stdlib_modules() for compatibility.

    Args:
        python_version: Python version tuple (kept for API compatibility).

    Returns:
        Set of standard library module names.
    """
    return get_stdlib_modules(python_version)


def _get_fallback_stdlib_modules() -> set[str]:
    """Fallback stdlib module list for Python < 3.10.

    This is a minimal set of common stdlib modules.
    Should not be used in practice as we require Python 3.10+.
    """
    return {
        # Core modules
        "abc",
        "aifc",
        "argparse",
        "array",
        "ast",
        "asynchat",
        "asyncio",
        "asyncore",
        "atexit",
        "audioop",
        "base64",
        "bdb",
        "binascii",
        "binhex",
        "bisect",
        "builtins",
        "bz2",
        "calendar",
        "cgi",
        "cgitb",
        "chunk",
        "cmath",
        "cmd",
        "code",
        "codecs",
        "codeop",
        "collections",
        "colorsys",
        "compileall",
        "concurrent",
        "configparser",
        "contextlib",
        "contextvars",
        "copy",
        "copyreg",
        "cProfile",
        "crypt",
        "csv",
        "ctypes",
        "curses",
        "dataclasses",
        "datetime",
        "dbm",
        "decimal",
        "difflib",
        "dis",
        "distutils",
        "doctest",
        "email",
        "encodings",
        "ensurepip",
        "enum",
        "errno",
        "faulthandler",
        "fcntl",
        "filecmp",
        "fileinput",
        "fnmatch",
        "fractions",
        "ftplib",
        "functools",
        "gc",
        "getopt",
        "getpass",
        "gettext",
        "glob",
        "graphlib",
        "grp",
        "gzip",
        "hashlib",
        "heapq",
        "hmac",
        "html",
        "http",
        "imaplib",
        "imghdr",
        "imp",
        "importlib",
        "inspect",
        "io",
        "ipaddress",
        "itertools",
        "json",
        "keyword",
        "lib2to3",
        "linecache",
        "locale",
        "logging",
        "lzma",
        "mailbox",
        "mailcap",
        "marshal",
        "math",
        "mimetypes",
        "mmap",
        "modulefinder",
        "msilib",
        "msvcrt",
        "multiprocessing",
        "netrc",
        "nis",
        "nntplib",
        "numbers",
        "operator",
        "optparse",
        "os",
        "ossaudiodev",
        "parser",
        "pathlib",
        "pdb",
        "pickle",
        "pickletools",
        "pipes",
        "pkgutil",
        "platform",
        "plistlib",
        "poplib",
        "posix",
        "posixpath",
        "pprint",
        "profile",
        "pstats",
        "pty",
        "pwd",
        "py_compile",
        "pyclbr",
        "pydoc",
        "queue",
        "quopri",
        "random",
        "re",
        "readline",
        "reprlib",
        "resource",
        "rlcompleter",
        "runpy",
        "sched",
        "secrets",
        "select",
        "selectors",
        "shelve",
        "shlex",
        "shutil",
        "signal",
        "site",
        "smtpd",
        "smtplib",
        "sndhdr",
        "socket",
        "socketserver",
        "spwd",
        "sqlite3",
        "ssl",
        "stat",
        "statistics",
        "string",
        "stringprep",
        "struct",
        "subprocess",
        "sunau",
        "symbol",
        "symtable",
        "sys",
        "sysconfig",
        "syslog",
        "tabnanny",
        "tarfile",
        "telnetlib",
        "tempfile",
        "termios",
        "test",
        "textwrap",
        "threading",
        "time",
        "timeit",
        "tkinter",
        "token",
        "tokenize",
        "tomllib",
        "trace",
        "traceback",
        "tracemalloc",
        "tty",
        "turtle",
        "turtledemo",
        "types",
        "typing",
        "unicodedata",
        "unittest",
        "urllib",
        "uu",
        "uuid",
        "venv",
        "warnings",
        "wave",
        "weakref",
        "webbrowser",
        "winreg",
        "winsound",
        "wsgiref",
        "xdrlib",
        "xml",
        "xmlrpc",
        "zipapp",
        "zipfile",
        "zipimport",
        "zlib",
        # Additional Python 3.10+ modules
        "zoneinfo",
    }
