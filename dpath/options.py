from os import environ

ALLOW_EMPTY_STRING_KEYS = False

ALLOW_REGEX = "ALLOW_REGEX" in environ
"""Enables regular expression support.

Enabling this feature will allow usage of regular expressions as part of paths.
Regular expressions must be wrapped in curly brackets. For example: "a/b/{[cd]}".
Expressions will be compiled using the standard library re.compile function.
"""

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
