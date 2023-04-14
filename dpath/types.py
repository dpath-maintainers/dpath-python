from enum import IntFlag, auto
from typing import Union, Any, Callable, Sequence, Tuple, List, Optional, MutableMapping


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


PathSegment = Union[int, str, bytes]
"""Type alias for dict path segments where integers are explicitly casted."""

Filter = Callable[[Any], bool]
"""Type alias for filter functions.

(Any) -> bool"""

Glob = Union[str, Sequence[str]]
"""Type alias for glob parameters."""

Path = Union[str, Sequence[PathSegment]]
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
