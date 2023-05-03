from enum import IntFlag, auto
from typing import Union, Any, Callable, Sequence, Tuple, List, Optional, MutableMapping
from re import Pattern
from abc import ABC
from dpath.options import PEP544_PROTOCOL_AVAILABLE

if PEP544_PROTOCOL_AVAILABLE:
    try:
        # Use PEP544 for Duck Typing style generalized match objects
        # Requires Python 3.8
        from typing import Protocol, runtime_checkable
        from abc import abstractmethod
    except Exception:
        PEP544_PROTOCOL_AVAILABLE = False


class SymmetricInt(int):
    """Same as a normal int but mimicks the behavior of list indexes (can be compared to a negative number)."""

    def __new__(cls, value: int, max_value: int, *args, **kwargs):
        if value >= max_value:
            raise TypeError(
                f"Tried to initiate a {cls.__name__} with a value ({value}) "
                f"greater than the provided max value ({max_value})"
            )

        obj = super().__new__(cls, value)
        obj.max_value = max_value

        return obj

    def __eq__(self, other):
        if not isinstance(other, int):
            return False

        if other >= self.max_value or other <= -self.max_value:
            return False

        return int(self) == (self.max_value + other) % self.max_value

    def __repr__(self):
        return f"<{self.__class__.__name__} {int(self)}%{self.max_value}>"

    def __str__(self):
        return str(int(self))


class MergeType(IntFlag):
    ADDITIVE = auto()
    """List objects are combined onto one long list (NOT a set). This is the default flag."""

    REPLACE = auto()
    """Instead of combining list objects, when 2 list objects are at an equal depth of merge, replace the destination \
    with the source."""

    TYPESAFE = auto()
    """When 2 keys at equal levels are of different types, raise a TypeError exception. By default, the source \
    replaces the destination in this situation."""


PathSegment = Union[int, str, bytes, Pattern]
"""Type alias for dict path segments where integers are explicitly casted."""

Filter = Callable[[Any], bool]
"""Type alias for filter functions.

(Any) -> bool"""


class Basic_StringMatcher (ABC):
    """ Base class to be used when typing.Protocol is not available, or if the user so chooses.
        (always supported).
        In this case, a derived class defining the method match can be used to match path components.
        (see examples)
    """

    def __init__(self):
        raise RuntimeError("This is a pseudo abstract class")

    def match(self, str):
        """ This must be provided by the user derived class to define a custom matcher
        Args:
            str ( str): the string to be matched
        Returns:
            None: the string does not match
            otherwise: the match is accepted, in particular False is not a rejection.
        """
        pass


if PEP544_PROTOCOL_AVAILABLE:
    # Introduced in Python 3.8

    @runtime_checkable
    class Duck_StringMatcher(Protocol):
        """ Permits match component matching using duck typing (see examples):
            The user must provide and object that defines the match method to
            implement the generalized matcher.

            Uses PEP 544: Protocols: Structural subtyping (static duck typing)
            to define requirements for a string matcher that can be used in
            an extended glob.

            Requirement:
             - match(str) -> Optional (Object)
        """
        @abstractmethod
        def match(self, str) -> Optional[object]:
            """ Requirement for match function, must return None if matching
            rejected. False is not a rejection !
            """
            pass

    StringMatcher = Union[Pattern, Duck_StringMatcher, Basic_StringMatcher]

    # for use with isinstance
    StringMatcher_astuple = (Pattern, Basic_StringMatcher, Duck_StringMatcher)
else:

    Duck_StringMatcher = Basic_StringMatcher

    StringMatcher = Union[Pattern, Basic_StringMatcher]
    """ Either a re.Pattern or a type that satisfies duck typing requirements
    for matching strings
    """

    # For use with isinstance. Apparently, isinstance ability to deal with Union
    # is not available before Python 3.10, see https://bugs.python.org/issue44529
    # and https://www.python.org/dev/peps/pep-0604/#isinstance-and-issubclass
    StringMatcher_astuple = (Pattern, Basic_StringMatcher)

"""Type alias for glob parameters, allows re.Pattern and generalized matchers"""
Glob = Union[str, Pattern, Sequence[Union[str, Pattern, StringMatcher]]]

Path = Union[str, Pattern, Sequence[PathSegment]]
"""Type alias for path parameters."""

Hints = Sequence[Tuple[PathSegment, type]]
"""Type alias for creator function hint sequences."""

Creator = Callable[[Union[MutableMapping, List], Path, int, Optional[Hints]], None]
"""Type alias for creator functions.

Example creator function signature:

    def creator(
        current: Union[MutableMapping, List],
        segments: Sequence[PathSegment],
        i: int,
        hints: Sequence[Tuple[PathSegment, type]] = ()
    )"""
