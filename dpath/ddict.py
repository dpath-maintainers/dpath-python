from copy import deepcopy
from typing import Any, MutableMapping

from dpath import Creator
from dpath.types import MergeType, Filter, Glob

_DEFAULT_SENTINEL: Any = object()


class DDict(dict):
    """
    Glob aware dict
    """

    def __init__(self, data: MutableMapping, __separator="/", __creator: Creator = None, **kwargs):
        super().__init__()
        super().update(data, **kwargs)

        self.separator = __separator
        self.creator = __creator

        self.recursive_items = True

    def __getitem__(self, item):
        return self.get(item)

    def __contains__(self, item):
        return len(self.search(item)) > 0

    def __setitem__(self, glob, value):
        from dpath import new

        # Prevent infinite recursion and other issues
        temp = dict(self)

        new(temp, glob, value, separator=self.separator, creator=self.creator)

        self.clear()
        self.update(temp)

    def __delitem__(self, glob: Glob, afilter: Filter = None):
        from dpath import delete

        temp = dict(self)

        delete(temp, glob, separator=self.separator, afilter=afilter)

        self.clear()
        self.update(temp)

    def __or__(self, other):
        from dpath import merge

        copy = deepcopy(self)
        return merge(copy, other, self.separator)

    def __ior__(self, other):
        return self.merge(other)

    def __len__(self):
        return sum(1 for _ in self.keys())

    def __repr__(self):
        return f"{type(self).__name__}({super().__repr__()})"

    def get(self, glob: Glob, default=_DEFAULT_SENTINEL) -> Any:
        """
        Same as dict.get but accepts glob aware keys.
        """
        from dpath import get

        if default is _DEFAULT_SENTINEL:
            # Let util.get handle default value
            return get(self, glob, separator=self.separator)
        else:
            # Default value was passed
            return get(self, glob, separator=self.separator, default=default)

    def setdefault(self, glob: Glob, __default=_DEFAULT_SENTINEL):
        if glob in self:
            return self[glob]

        self[glob] = None if __default == _DEFAULT_SENTINEL else __default
        return self[glob]

    def pop(self, glob: Glob):
        results = self.search(glob)
        del self[glob]
        return results

    def search(self, glob: Glob, yielded=False, afilter: Filter = None, dirs=True):
        from dpath import search

        return search(self, glob, yielded=yielded, separator=self.separator, afilter=afilter, dirs=dirs)

    def merge(self, src: MutableMapping, afilter: Filter = None, flags=MergeType.ADDITIVE):
        """
        Performs in-place merge with another dict.
        """
        from dpath import merge

        result = merge(self, src, separator=self.separator, afilter=afilter, flags=flags)

        self.update(result)

        return self

    def keys(self):
        from dpath.segments import walk

        if not self.recursive_items:
            yield from dict(self).keys()
            return

        for path, _ in walk(self):
            yield self.separator.join((str(segment) for segment in path))

    def values(self):
        from dpath.segments import walk

        d = self
        if not self.recursive_items:
            d = dict(self)

        for _, value in walk(d):
            yield value

    def walk(self):
        """
        Yields all possible key, value pairs.
        """
        from dpath.segments import walk

        for path, value in walk(self):
            yield self.separator.join((str(segment) for segment in path)), value
