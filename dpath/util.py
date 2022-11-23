import warnings
from typing import Any, Dict

import dpath
from dpath import _DEFAULT_SENTINEL
from dpath.types import Filter, Creator, MergeType


def deprecated(func):
    message = \
        "The dpath.util package is being deprecated. All util functions have been moved to dpath package top level."

    def wrapper(*args, **kwargs):
        warnings.warn(message, DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)

    return wrapper


@deprecated
def new(obj: Dict, path: str, value, separator="/", creator: Creator = None) -> Dict:
    return dpath.new(obj, path, value, separator, creator)


@deprecated
def delete(obj: Dict, glob: str, separator="/", afilter: Filter = None) -> int:
    return dpath.delete(obj, glob, separator, afilter)


@deprecated
def set(obj: Dict, glob: str, value, separator="/", afilter: Filter = None) -> int:
    return dpath.set(obj, glob, value, separator, afilter)


@deprecated
def get(obj: Dict, glob: str, separator="/", default: Any = _DEFAULT_SENTINEL) -> Dict:
    return dpath.get(obj, glob, separator, default)


@deprecated
def values(obj: Dict, glob: str, separator="/", afilter: Filter = None, dirs=True):
    return dpath.values(obj, glob, separator, afilter, dirs)


@deprecated
def search(obj: Dict, glob: str, yielded=False, separator="/", afilter: Filter = None, dirs=True):
    return dpath.search(obj, glob, yielded, separator, afilter, dirs)


@deprecated
def merge(dst: Dict, src: Dict, separator="/", afilter: Filter = None, flags=MergeType.ADDITIVE):
    return dpath.merge(dst, src, separator, afilter, flags),
