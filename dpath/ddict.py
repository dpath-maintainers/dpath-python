from typing import Callable, Any, List, Dict

from dpath import util
from dpath.util import MERGE_ADDITIVE

FilterType = Callable[[Any], bool]  # (Any) -> bool

_DEFAULT_SENTINEL: Any = object()


class DDict(dict):
    """
    Glob aware dict
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set(self, glob: str, value, separator="/", afilter: FilterType = None):
        return util.set(self, glob, value, separator=separator, afilter=afilter)

    def get(self, glob: str, separator="/", default=_DEFAULT_SENTINEL) -> Any:
        """
        Same as dict.get but glob aware
        """
        if default is not _DEFAULT_SENTINEL:
            # Default value was passed
            return util.get(self, glob, separator=separator, default=default)
        else:
            # Let util.get handle default value
            return util.get(self, glob, separator=separator)

    def values(self, glob="*", separator="/", afilter: FilterType = None, dirs=True) -> List:
        """
        Same as dict.values but glob aware
        """
        return util.values(self, glob, separator=separator, afilter=afilter, dirs=dirs)

    def search(self, glob, yielded=False, separator="/", afilter: FilterType = None, dirs=True):
        return util.search(self, glob, yielded=yielded, separator=separator, afilter=afilter, dirs=dirs)

    def merge(self, src: Dict, separator="/", afilter: FilterType = None, flags=MERGE_ADDITIVE):
        return util.merge(self, src, separator=separator, afilter=afilter, flags=flags)
