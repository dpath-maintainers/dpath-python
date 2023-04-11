
ALLOW_EMPTY_STRING_KEYS = False

#  Extension to interpret path segments "{rrr}" as re.regexp "rrr" enabled by default.
#  Disable to preserve backwards compatibility in the case where a user has a
#  path "a/b/{cd}" where the brackets are intentional and do not denote a request
#  to re.compile cd
DPATH_ACCEPT_RE_REGEXP = True

# --------------------------------------------------------------------
# Language processor and library variations
# --------------------------------------------------------------------

# PEP544_PROTOCOL_AVAILABLE indicates that the language processor permits duck typing
# PEP-0544 by defining typing.Protocol. (Introduced in Python 3.8)
# See https://peps.python.org/pep-0544/.
# Otherwise provide a fall back using a derived class technique.
try:
    from typing import Protocol
    PEP544_PROTOCOL_AVAILABLE = True
    assert type(Protocol) != int   # inserted to quiesce flake8 (F401) !!!
except Exception:
    PEP544_PROTOCOL_AVAILABLE = False
