""" The module dpath.options defines
    - ALLOW_EMPTY_STRING_KEYS
    - PATH_ACCEPT_RE_REGEXP  : permits selection of option to accept regular
                               expressions in paths
    - PEP544_PROTOCOL_AVAILABLE: the language processor permits duck typing
                             PEP-0544
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

# Enable usage of PEP544 / typing.Protocol if available
# see https://peps.python.org/pep-0544/
# this allows usage of typing module's:
#       Protocol, runtime_checkable
#  and from abc: abstractmethod
# We made the choice of discovering by testing in a try block;
# the may then use dpath.options.PEP544_PROTOCOL_AVAILABLE to figure out

try:
    from typing import Protocol
    PEP544_PROTOCOL_AVAILABLE = True
except Exception:
    PEP544_PROTOCOL_AVAILABLE = False

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


def isinstance_ext(o, t):
    """ allows to use Unions as insinstance reference type
    """
    if (type(t) == type(Union[str, int])) and not ISINSTANCE_ACCEPTS_UNIONS:
        return any(map(lambda x: isinstance(o, x), t))

    return isinstance(o, t)
