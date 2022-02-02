from collections.abc import MutableMapping, MutableSequence
from enum import IntFlag, auto
from typing import Union, List, Any, Dict, Callable, Sequence, Tuple, Optional

from dpath import options, segments
from dpath.exceptions import InvalidKeyName, PathNotFound

_DEFAULT_SENTINEL = object()


class MergeType(IntFlag):
    ADDITIVE = auto()
    """List objects are combined onto one long list (NOT a set). This is the default flag."""

    REPLACE = auto()
    """Instead of combining list objects, when 2 list objects are at an equal depth of merge, replace the destination 
    with the source."""

    TYPESAFE = auto()
    """When 2 keys at equal levels are of different types, raise a TypeError exception. By default, the source 
    replaces the destination in this situation."""


PathSegment = Union[int, str]
"""Type alias for dict path segments where integers are explicitly casted."""

Filter = Callable[[Any], bool]
"""Type alias for filter functions.

(Any) -> bool"""

Hints = Sequence[Tuple[PathSegment, type]]
"""Type alias for creator function hint sequences."""

Creator = Callable[[Union[Dict, List], Sequence[PathSegment], int, Optional[Hints]], None]
"""Type alias for creator functions.

Example creator function signature:
    
    def creator(
        current: Union[Dict, List],
        segments: Sequence[PathSegment],
        i: int,
        hints: Sequence[Tuple[PathSegment, type]] = ()
    )"""


def _split_path(path: str, separator: str) -> Union[List[PathSegment], PathSegment]:
    """
    Given a path and separator, return a tuple of segments. If path is
    already a non-leaf thing, return it.

    Note that a string path with the separator at index[0] will have the
    separator stripped off. If you pass a list path, the separator is
    ignored, and is assumed to be part of each key glob. It will not be
    stripped.
    """
    if not segments.leaf(path):
        split_segments = path
    else:
        split_segments = path.lstrip(separator).split(separator)

        if options.CONVERT_INT_LIKE_SEGMENTS:
            # Attempt to convert integer segments into actual integers.
            final = []
            for segment in split_segments:
                try:
                    final.append(int(segment))
                except:
                    final.append(segment)
            split_segments = final

    return split_segments


def new(obj: Dict, path: str, value, separator="/", creator: Creator = None) -> Dict:
    """
    Set the element at the terminus of path to value, and create
    it if it does not exist (as opposed to 'set' that can only
    change existing keys).

    path will NOT be treated like a glob. If it has globbing
    characters in it, they will become part of the resulting
    keys

    creator allows you to pass in a creator method that is
    responsible for creating missing keys at arbitrary levels of
    the path (see the help for dpath.path.set)
    """
    split_segments = _split_path(path, separator)
    if creator:
        return segments.set(obj, split_segments, value, creator=creator)
    return segments.set(obj, split_segments, value)


def delete(obj: Dict, glob: str, separator="/", afilter: Filter = None) -> int:
    """
    Given a obj, delete all elements that match the glob.

    Returns the number of deleted objects. Raises PathNotFound if no paths are
    found to delete.
    """
    globlist = _split_path(glob, separator)

    def f(obj, pair, counter):
        (path_segments, value) = pair

        # Skip segments if they no longer exist in obj.
        if not segments.has(obj, path_segments):
            return

        matched = segments.match(path_segments, globlist)
        selected = afilter and segments.leaf(value) and afilter(value)

        if (matched and not afilter) or selected:
            key = path_segments[-1]
            parent = segments.get(obj, path_segments[:-1])

            try:
                # Attempt to treat parent like a sequence.
                parent[0]

                if len(parent) - 1 == key:
                    # Removing the last element of a sequence. It can be
                    # truly removed without affecting the ordering of
                    # remaining items.
                    #
                    # Note: In order to achieve proper behavior we are
                    # relying on the reverse iteration of
                    # non-dictionaries from segments.kvs().
                    # Otherwise we'd be unable to delete all the tails
                    # of a list and end up with None values when we
                    # don't need them.
                    del parent[key]
                else:
                    # This key can't be removed completely because it
                    # would affect the order of items that remain in our
                    # result.
                    parent[key] = None
            except:
                # Attempt to treat parent like a dictionary instead.
                del parent[key]

            counter[0] += 1

    [deleted] = segments.foldm(obj, f, [0])
    if not deleted:
        raise PathNotFound(f"Could not find {glob} to delete it")

    return deleted


def set(obj: Dict, glob: str, value, separator="/", afilter: Filter = None) -> int:
    """
    Given a path glob, set all existing elements in the document
    to the given value. Returns the number of elements changed.
    """
    globlist = _split_path(glob, separator)

    def f(obj, pair, counter):
        (path_segments, found) = pair

        # Skip segments if they no longer exist in obj.
        if not segments.has(obj, path_segments):
            return

        matched = segments.match(path_segments, globlist)
        selected = afilter and segments.leaf(found) and afilter(found)

        if (matched and not afilter) or (matched and selected):
            segments.set(obj, path_segments, value, creator=None)
            counter[0] += 1

    [changed] = segments.foldm(obj, f, [0])
    return changed


def get(obj: Dict, glob: str, separator="/", default: Any = _DEFAULT_SENTINEL) -> Dict:
    """
    Given an object which contains only one possible match for the given glob,
    return the value for the leaf matching the given glob.
    If the glob is not found and a default is provided,
    the default is returned.

    If more than one leaf matches the glob, ValueError is raised. If the glob is
    not found and a default is not provided, KeyError is raised.
    """
    if glob == "/":
        return obj

    globlist = _split_path(glob, separator)

    def f(_, pair, results):
        (path_segments, found) = pair

        if segments.match(path_segments, globlist):
            results.append(found)
        if len(results) > 1:
            return False

    results = segments.fold(obj, f, [])

    if len(results) == 0:
        if default is not _DEFAULT_SENTINEL:
            return default

        raise KeyError(glob)
    elif len(results) > 1:
        raise ValueError(f"dpath.util.get() globs must match only one leaf: {glob}")

    return results[0]


def values(obj: Dict, glob: str, separator="/", afilter: Filter = None, dirs=True):
    """
    Given an object and a path glob, return an array of all values which match
    the glob. The arguments to this function are identical to those of search().
    """
    yielded = True

    return [v for p, v in search(obj, glob, yielded, separator, afilter, dirs)]


def search(obj: Dict, glob: str, yielded=False, separator="/", afilter: Filter = None, dirs=True):
    """
    Given a path glob, return a dictionary containing all keys
    that matched the given glob.

    If 'yielded' is true, then a dictionary will not be returned.
    Instead tuples will be yielded in the form of (path, value) for
    every element in the document that matched the glob.
    """

    split_glob = _split_path(glob, separator)

    def keeper(path, found):
        """
        Generalized test for use in both yielded and folded cases.
        Returns True if we want this result. Otherwise returns False.
        """
        if not dirs and not segments.leaf(found):
            return False

        matched = segments.match(path, split_glob)
        selected = afilter and afilter(found)

        return (matched and not afilter) or (matched and selected)

    if yielded:
        def yielder():
            for path, found in segments.walk(obj):
                if keeper(path, found):
                    yield separator.join(map(segments.int_str, path)), found
        return yielder()
    else:
        def f(obj, pair, result):
            (path, found) = pair

            if keeper(path, found):
                segments.set(result, path, found, hints=segments.types(obj, path))

        return segments.fold(obj, f, {})


def merge(dst: Dict, src: Dict, separator="/", afilter: Filter = None, flags=MergeType.ADDITIVE):
    """
    Merge source into destination. Like dict.update() but performs deep
    merging.

    NOTE: This does not do a deep copy of the source object. Applying merge
    will result in references to src being present in the dst tree. If you do
    not want src to potentially be modified by other changes in dst (e.g. more
    merge calls), then use a deep copy of src.

    NOTE that merge() does NOT copy objects - it REFERENCES. If you merge
    take these two dictionaries:

    >>> a = {'a': [0] }
    >>> b = {'a': [1] }

    ... and you merge them into an empty dictionary, like so:

    >>> d = {}
    >>> dpath.util.merge(d, a)
    >>> dpath.util.merge(d, b)

    ... you might be surprised to find that a['a'] now contains [0, 1].
    This is because merge() says (d['a'] = a['a']), and thus creates a reference.
    This reference is then modified when b is merged, causing both d and
    a to have ['a'][0, 1]. To avoid this, make your own deep copies of source
    objects that you intend to merge. For further notes see
    https://github.com/akesterson/dpath-python/issues/58

    flags is an OR'ed combination of MergeType enum members.
    """
    filtered_src = search(src, '**', afilter=afilter, separator='/')

    def are_both_mutable(o1, o2):
        mapP = isinstance(o1, MutableMapping) and isinstance(o2, MutableMapping)
        seqP = isinstance(o1, MutableSequence) and isinstance(o2, MutableSequence)

        if mapP or seqP:
            return True

        return False

    def merger(dst, src, _segments=()):
        for key, found in segments.make_walkable(src):
            # Our current path in the source.
            current_path = _segments + (key,)

            if len(key) == 0 and not options.ALLOW_EMPTY_STRING_KEYS:
                raise InvalidKeyName("Empty string keys not allowed without "
                                     "dpath.options.ALLOW_EMPTY_STRING_KEYS=True: "
                                     f"{current_path}")

            # Validate src and dst types match.
            if flags & MergeType.TYPESAFE:
                if segments.has(dst, current_path):
                    target = segments.get(dst, current_path)
                    tt = type(target)
                    ft = type(found)
                    if tt != ft:
                        path = separator.join(current_path)
                        raise TypeError(f"Cannot merge objects of type {tt} and {ft} at {path}")

            # Path not present in destination, create it.
            if not segments.has(dst, current_path):
                segments.set(dst, current_path, found)
                continue

            # Retrieve the value in the destination.
            target = segments.get(dst, current_path)

            # If the types don't match, replace it.
            if type(found) != type(target) and not are_both_mutable(found, target):
                segments.set(dst, current_path, found)
                continue

            # If target is a leaf, the replace it.
            if segments.leaf(target):
                segments.set(dst, current_path, found)
                continue

            # At this point we know:
            #
            # * The target exists.
            # * The types match.
            # * The target isn't a leaf.
            #
            # Pretend we have a sequence and account for the flags.
            try:
                if flags & MergeType.ADDITIVE:
                    target += found
                    continue

                if flags & MergeType.REPLACE:
                    try:
                        target[""]
                    except TypeError:
                        segments.set(dst, current_path, found)
                        continue
                    except:
                        raise
            except:
                # We have a dictionary like thing and we need to attempt to
                # recursively merge it.
                merger(dst, found, current_path)

    merger(dst, filtered_src)

    return dst
