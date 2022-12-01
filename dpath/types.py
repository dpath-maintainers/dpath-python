from enum import IntFlag, auto
from typing import Union, Any, Callable, Sequence, Tuple, List, Optional, MutableMapping


class CyclicInt(int):
    """Same as a normal int but mimicks the behavior of list indexes (can be compared to a negative number)"""

    def __new__(cls, value, max_value, *args, **kwargs):
        if value >= max_value:
            raise TypeError(
                f"Tried to initiate a CyclicInt with a value ({value}) "
                f"greater than the provided max value ({max_value})"
            )

        obj = super().__new__(cls, value)
        obj.max_value = max_value

        return obj

    def __eq__(self, other):
        return int(self) == (self.max_value + other) % self.max_value

    def __repr__(self):
        return f"<CyclicInt {int(self)}/{self.max_value}>"


class MergeType(IntFlag):
    ADDITIVE = auto()
    """List objects are combined onto one long list (NOT a set). This is the default flag."""

    REPLACE = auto()
    """Instead of combining list objects, when 2 list objects are at an equal depth of merge, replace the destination \
    with the source."""

    TYPESAFE = auto()
    """When 2 keys at equal levels are of different types, raise a TypeError exception. By default, the source \
    replaces the destination in this situation."""


PathSegment = Union[int, str]
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
