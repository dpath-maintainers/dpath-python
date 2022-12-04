from typing import Any, MutableMapping

from dpath import MergeType, merge, search, values, get, set, Filter, Glob

_DEFAULT_SENTINEL: Any = object()


class DDict(dict):
    """
    Glob aware dict
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set(self, glob: Glob, value, separator="/", afilter: Filter = None):
        return set(self, glob, value, separator=separator, afilter=afilter)

    def get(self, glob: Glob, separator="/", default=_DEFAULT_SENTINEL) -> Any:
        """
        Same as dict.get but glob aware
        """
        if default is not _DEFAULT_SENTINEL:
            # Default value was passed
            return get(self, glob, separator=separator, default=default)
        else:
            # Let util.get handle default value
            return get(self, glob, separator=separator)

    def values(self, glob: Glob = "*", separator="/", afilter: Filter = None, dirs=True):
        """
        Same as dict.values but glob aware
        """
        return values(self, glob, separator=separator, afilter=afilter, dirs=dirs)

    def search(self, glob: Glob, yielded=False, separator="/", afilter: Filter = None, dirs=True):
        return search(self, glob, yielded=yielded, separator=separator, afilter=afilter, dirs=dirs)

    def merge(self, src: MutableMapping, separator="/", afilter: Filter = None, flags=MergeType.ADDITIVE):
        return merge(self, src, separator=separator, afilter=afilter, flags=flags)
