""" The module dpath.options defines
    - ALLOW_EMPTY_STRING_KEYS
    - PATH_ACCEPT_RE_REGEXP  : permits selection of option to accept regular
                               expressions in paths
    - ISINSTANCE_ACCEPTS_UNIONS: isinstance can use types which are Unions
    - (Internal) DEBUG_PRINT : select additional printout from environment
                               PYTHON_DPATH_DEBUG
"""
from sys import stderr
from os import getenv
from typing import Union

DEBUG_PRINT = True if getenv("PYTHON_DPATH_DEBUG") is not None else False

ALLOW_EMPTY_STRING_KEYS = False

# extension disabled by default to preserve backwards compatibility
#
DPATH_ACCEPT_RE_REGEXP = False

# --------------------------------------------------------------------
# Language processor variations
# --------------------------------------------------------------------

# Using Unions of types in isinstance is also an issue
# https://peps.python.org/pep-0604/#isinstance-and-issubclass
# https://bugs.python.org/issue44529

try:
    _PS = Union[int, str]
    a = isinstance(2, _PS)
    ISINSTANCE_ACCEPTS_UNIONS = True
    if DEBUG_PRINT:
        print(f"OK for isinstance with Unions: returns {a}", file=stderr)
except Exception as err:
    ISINSTANCE_ACCEPTS_UNIONS = False
    if DEBUG_PRINT:
        print(f"NOT OK for isinstance with Unions: {err}", file=stderr)
