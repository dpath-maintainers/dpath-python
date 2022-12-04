from typing import Any, MutableMapping

from dpath import Creator
from dpath.types import MergeType, Filter, Glob

_DEFAULT_SENTINEL: Any = object()


class DDict(dict):
    """
    Glob aware dict
    """

    def __init__(self, data: MutableMapping, separator="/", creator: Creator = None):
        super().__init__(data)

        self.separator = separator
        self.creator = creator

    def __getitem__(self, item):
        return self.get(item)

    def __contains__(self, item):
        return len(self.search(item)) > 0

    def __setitem__(self, key, value):
        from dpath import new

        # Prevent infinite recursion and other issues
        temp = dict(self)

        new(temp, key, value, separator=self.separator, creator=self.creator)

        self.update(temp)

    def __len__(self):
        return len(self.keys())

    def __or__(self, other):
        return self.merge(other)

    def get(self, glob: Glob, default=_DEFAULT_SENTINEL) -> Any:
        """
        Same as dict.get but glob aware
        """
        from dpath import get

        if default is _DEFAULT_SENTINEL:
            # Let util.get handle default value
            return get(self, glob, separator=self.separator)
        else:
            # Default value was passed
            return get(self, glob, separator=self.separator, default=default)

    # def keys(self):
    #     from dpath.segments import walk
    #
    #     temp = dict(self)
    #
    #     paths = (part[0] for part in walk(temp))
    #     return (self.separator.join((str(segment) for segment in path)) for path in paths)

    def values(self, glob: Glob = "*", afilter: Filter = None, dirs=True):
        """
        Same as dict.values but glob aware
        """
        from dpath import values

        return values(self, glob, separator=self.separator, afilter=afilter, dirs=dirs)

    def search(self, glob: Glob, yielded=False, afilter: Filter = None, dirs=True):
        from dpath import search

        return search(self, glob, yielded=yielded, separator=self.separator, afilter=afilter, dirs=dirs)

    def merge(self, src: MutableMapping, afilter: Filter = None, flags=MergeType.ADDITIVE):
        from dpath import merge

        temp = dict(self)

        result = merge(temp, src, separator=self.separator, afilter=afilter, flags=flags)

        self.update(result)

        return self

    def items(self):
        from dpath.segments import walk

        temp = dict(self)

        for path, value in walk(temp):
            yield self.separator.join((str(segment) for segment in path)), value
