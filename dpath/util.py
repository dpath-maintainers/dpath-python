from collections.abc import MutableMapping
from collections.abc import MutableSequence
from dpath import options
from dpath.exceptions import InvalidKeyName
import dpath.segments

_DEFAULT_SENTINAL = object()
MERGE_REPLACE = (1 << 1)
MERGE_ADDITIVE = (1 << 2)
MERGE_TYPESAFE = (1 << 3)

def __safe_path__(path, separator):
    '''
    Given a path and separator, return a tuple of segments. If path is
    already a non-leaf thing, return it.

    Note that a string path with the separator at index[0] will have the
    separator stripped off. If you pass a list path, the separator is
    ignored, and is assumed to be part of each key glob. It will not be
    stripped.
    '''
    if not dpath.segments.leaf(path):
        segments = path
    else:
        segments = path.lstrip(separator).split(separator)

        # FIXME: This check was in the old internal library, but I can't
        # see a way it could fail...
        for i, segment in enumerate(segments):
            if (separator and (separator in segment)):
                raise InvalidKeyName("{} at {}[{}] contains the separator '{}'"
                                     "".format(segment, segments, i, separator))

        # Attempt to convert integer segments into actual integers.
        final = []
        for segment in segments:
            try:
                final.append(int(segment))
            except:
                final.append(segment)
        segments = final

    return segments


def new(obj, path, value, separator='/', creator=None):
    '''
    Set the element at the terminus of path to value, and create
    it if it does not exist (as opposed to 'set' that can only
    change existing keys).

    path will NOT be treated like a glob. If it has globbing
    characters in it, they will become part of the resulting
    keys

    creator allows you to pass in a creator method that is
    responsible for creating missing keys at arbitrary levels of
    the path (see the help for dpath.path.set)
    '''
    segments = __safe_path__(path, separator)
    if creator:
        return dpath.segments.set(obj, segments, value, creator=creator)
    return dpath.segments.set(obj, segments, value)


def delete(obj, glob, separator='/', afilter=None):
    '''
    Given a obj, delete all elements that match the glob.

    Returns the number of deleted objects. Raises PathNotFound if no paths are
    found to delete.
    '''
    globlist = __safe_path__(glob, separator)

    def f(obj, pair, counter):
        (segments, value) = pair

        # Skip segments if they no longer exist in obj.
        if not dpath.segments.has(obj, segments):
            return

        matched = dpath.segments.match(segments, globlist)
        selected = afilter and dpath.segments.leaf(value) and afilter(value)

        if (matched and not afilter) or selected:
            key = segments[-1]
            parent = dpath.segments.get(obj, segments[:-1])

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
                    # non-dictionaries from dpath.segments.kvs().
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

    [deleted] = dpath.segments.foldm(obj, f, [0])
    if not deleted:
        raise dpath.exceptions.PathNotFound("Could not find {0} to delete it".format(glob))

    return deleted


def set(obj, glob, value, separator='/', afilter=None):
    '''
    Given a path glob, set all existing elements in the document
    to the given value. Returns the number of elements changed.
    '''
    globlist = __safe_path__(glob, separator)

    def f(obj, pair, counter):
        (segments, found) = pair

        # Skip segments if they no longer exist in obj.
        if not dpath.segments.has(obj, segments):
            return

        matched = dpath.segments.match(segments, globlist)
        selected = afilter and dpath.segments.leaf(found) and afilter(found)

        if (matched and not afilter) or (matched and selected):
            dpath.segments.set(obj, segments, value, creator=None)
            counter[0] += 1

    [changed] = dpath.segments.foldm(obj, f, [0])
    return changed


def get(obj, glob, separator='/', default=_DEFAULT_SENTINAL):
    '''
    Given an object which contains only one possible match for the given glob,
    return the value for the leaf matching the given glob.
    If the glob is not found and a default is provided,
    the default is returned.

    If more than one leaf matches the glob, ValueError is raised. If the glob is
    not found and a default is not provided, KeyError is raised.
    '''
    if glob == '/':
        return obj

    globlist = __safe_path__(glob, separator)

    def f(obj, pair, results):
        (segments, found) = pair

        if dpath.segments.match(segments, globlist):
            results.append(found)
        if len(results) > 1:
            return False

    results = dpath.segments.fold(obj, f, [])

    if len(results) == 0:
        if default  is not _DEFAULT_SENTINAL:
            return default

        raise KeyError(glob)
    elif len(results) > 1:
        raise ValueError("dpath.util.get() globs must match only one leaf : %s" % glob)

    return results[0]


def values(obj, glob, separator='/', afilter=None, dirs=True):
    '''
    Given an object and a path glob, return an array of all values which match
    the glob. The arguments to this function are identical to those of search().
    '''
    yielded = True

    return [v for p, v in search(obj, glob, yielded, separator, afilter, dirs)]


def search(obj, glob, yielded=False, separator='/', afilter=None, dirs=True):
    '''
    Given a path glob, return a dictionary containing all keys
    that matched the given glob.

    If 'yielded' is true, then a dictionary will not be returned.
    Instead tuples will be yielded in the form of (path, value) for
    every element in the document that matched the glob.
    '''

    globlist = __safe_path__(glob, separator)

    def keeper(segments, found):
        '''
        Generalized test for use in both yielded and folded cases.
        Returns True if we want this result. Otherwise returns False.
        '''
        if not dirs and not dpath.segments.leaf(found):
            return False

        matched = dpath.segments.match(segments, globlist)
        selected = afilter and afilter(found)

        return (matched and not afilter) or (matched and selected)

    if yielded:
        def yielder():
            for segments, found in dpath.segments.walk(obj):
                if keeper(segments, found):
                    yield (separator.join(map(dpath.segments.int_str, segments)), found)
        return yielder()
    else:
        def f(obj, pair, result):
            (segments, found) = pair

            if keeper(segments, found):
                dpath.segments.set(result, segments, found, hints=dpath.segments.types(obj, segments))

        return dpath.segments.fold(obj, f, {})


def merge(dst, src, separator='/', afilter=None, flags=MERGE_ADDITIVE):
    '''
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

    flags is an OR'ed combination of MERGE_ADDITIVE, MERGE_REPLACE,
    MERGE_TYPESAFE.
        * MERGE_ADDITIVE : List objects are combined onto one long
          list (NOT a set). This is the default flag.
        * MERGE_REPLACE : Instead of combining list objects, when
          2 list objects are at an equal depth of merge, replace
          the destination with the source.
        * MERGE_TYPESAFE : When 2 keys at equal levels are of different
          types, raise a TypeError exception. By default, the source
          replaces the destination in this situation.
    '''
    filtered_src = search(src, '**', afilter=afilter, separator='/')

    def are_both_mutable(o1, o2):
        mapP = isinstance(o1, MutableMapping) and isinstance(o2, MutableMapping)
        seqP = isinstance(o1, MutableSequence) and isinstance(o2, MutableSequence)

        if mapP or seqP:
            return True

        return False

    def merger(dst, src, _segments=()):
        for key, found in dpath.segments.kvs(src):
            # Our current path in the source.
            segments = _segments + (key,)

            if len(key) == 0 and not options.ALLOW_EMPTY_STRING_KEYS:
                raise InvalidKeyName("Empty string keys not allowed without "
                                     "dpath.options.ALLOW_EMPTY_STRING_KEYS=True: "
                                     "{}".format(segments))

            # Validate src and dst types match.
            if flags & MERGE_TYPESAFE:
                if dpath.segments.has(dst, segments):
                    target = dpath.segments.get(dst, segments)
                    tt = type(target)
                    ft = type(found)
                    if tt != ft:
                        path = separator.join(segments)
                        raise TypeError("Cannot merge objects of type"
                                        "{0} and {1} at {2}"
                                        "".format(tt, ft, path))

            # Path not present in destination, create it.
            if not dpath.segments.has(dst, segments):
                dpath.segments.set(dst, segments, found)
                continue

            # Retrieve the value in the destination.
            target = dpath.segments.get(dst, segments)

            # If the types don't match, replace it.
            if ((type(found) != type(target)) and (not are_both_mutable(found, target))):
                dpath.segments.set(dst, segments, found)
                continue

            # If target is a leaf, the replace it.
            if dpath.segments.leaf(target):
                dpath.segments.set(dst, segments, found)
                continue

            # At this point we know:
            #
            # * The target exists.
            # * The types match.
            # * The target isn't a leaf.
            #
            # Pretend we have a sequence and account for the flags.
            try:
                if flags & MERGE_ADDITIVE:
                    target += found
                    continue

                if flags & MERGE_REPLACE:
                    try:
                        target['']
                    except TypeError:
                        dpath.segments.set(dst, segments, found)
                        continue
                    except:
                        raise
            except:
                # We have a dictionary like thing and we need to attempt to
                # recursively merge it.
                merger(dst, found, segments)

    merger(dst, filtered_src)

    return dst
