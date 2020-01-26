from copy import deepcopy
from dpath.exceptions import InvalidGlob, InvalidKeyName, PathNotFound
from dpath import options
from fnmatch import fnmatchcase


def kvs(node):
    '''
    Return a (key, value) iterator for the node.

    kvs(node) -> (generator -> (key, value))
    '''
    try:
        return iter(node.items())
    except AttributeError:
        return zip(range(len(node)), node)


def leaf(thing):
    '''
    Return True if thing is a leaf, otherwise False.

    leaf(thing) -> bool
    '''
    leaves = (bytes, str, int, float, bool, type(None))

    return isinstance(thing, leaves)


def leafy(thing):
    '''
    Same as leaf(thing), but also treats empty sequences and
    dictionaries as True.

    leafy(thing) -> bool
    '''
    return leaf(thing) or len(thing) == 0


def walk(obj, location=()):
    '''
    Yield all valid (segments, value) pairs (from a breadth-first
    search, right-to-left on sequences).

    walk(obj) -> (generator -> (segments, value))
    '''
    if not leaf(obj):
        for k, v in kvs(obj):
            length = None

            try:
                length = len(k)
            except:
                pass

            if length is not None and length == 0 and not options.ALLOW_EMPTY_STRING_KEYS:
                raise InvalidKeyName("Empty string keys not allowed without "
                                     "dpath.options.ALLOW_EMPTY_STRING_KEYS=True: "
                                     "{}".format(location + (k,)))
            yield ((location + (k,)), v)
        for k, v in kvs(obj):
            for found in walk(v, location + (k,)):
                yield found


def get(obj, segments):
    '''
    Return the value at the path indicated by segments.

    get(obj, segments) -> value
    '''
    current = obj
    for (i, segment) in enumerate(segments):
        if leaf(current):
            raise PathNotFound('Path: {}[{}]'.format(segments, i))

        current = current[segment]
    return current


def has(obj, segments):
    '''
    Return True if the path exists in the obj. Otherwise return False.

    has(obj, segments) -> bool
    '''
    try:
        get(obj, segments)
        return True
    except:
        return False


def expand(segments):
    '''
    Yield a tuple of segments for each possible length of segments.
    Starting from the shortest length of segments and increasing by 1.

    expand(keys) -> (..., keys[:-2], keys[:-1])
    '''
    index = 0
    for segment in segments:
        index += 1
        yield segments[:index]


def types(obj, segments):
    '''
    For each segment produce a tuple of (segment, type(value)).

    types(obj, segments) -> ((segment[0], type0), (segment[1], type1), ...)
    '''
    result = []
    for depth in expand(segments):
        result.append((depth[-1], type(get(obj, depth))))
    return tuple(result)


def leaves(obj):
    '''
    Yield all leaves as (segment, value) pairs.

    leaves(obj) -> (generator -> (segment, value))
    '''
    return filter(lambda p: leafy(p[1]), walk(obj))


def int_str(segment):
    '''
    If the segment is an integer, return the string conversion.
    Otherwise return the segment unchanged. The conversion uses 'str'
    which means that:

        * in Python 2.x: 0 -> b'0'
        * in Python 3.x: 0 -> u'0'

    int_str(segment) -> str
    '''
    if isinstance(segment, int):
        return str(segment)
    return segment


class Star(object):
    '''
    Used to create a global STAR symbol for tracking stars added when
    expanding star-star globs.
    '''
    pass


STAR = Star()


def match(segments, glob):
    '''
    Return True if the segments match the given glob, otherwise False.

    For the purposes of matching, integers are converted to their string
    equivalent (via str(segment)). This conversion happens on both the
    segments and the glob. This implies you cannot (with this function)
    differentiate a list index 0 from a dictionary key '0'.

    Star-star segments are a special case in that they will expand to 0
    or more star segments and the type will be coerced to match that of
    the segment.

    A segment is considered to match a glob if the function
    fnmatch.fnmatchcase returns True. If fnmatchcase returns False or
    throws an exception the result will be False.

    A Word of Caution:

    *** Globs can have different results between Python 2.x and 3.x. ***

    fnmatchcase differs in behavior between Python 2.x and 3.x with
    regard to handling comparison between different types (e.g. bytes
    and unicode). In 2.x it will attempt the comparison implicitly
    converting, but in 3.x it will throw an exception.

    match(segments, glob) -> bool
    '''
    segments = tuple(segments)
    glob = tuple(glob)

    path_len = len(segments)
    glob_len = len(glob)

    # Index of the star-star in the glob.
    ss = -1
    # The star-star normalized glob ('**' has been removed).
    ss_glob = glob

    if '**' in glob:
        ss = glob.index('**')
        if '**' in glob[ss + 1:]:
            raise InvalidGlob("Invalid glob. Only one '**' is permitted per glob: {}"
                              "".format(glob))

        # Convert '**' segment into multiple '*' segments such that the
        # lengths of the path and glob match. '**' also can collapse and
        # result in the removal of 1 segment.
        if path_len >= glob_len:
            # Path and glob have the same number of stars or the glob
            # needs more stars (which we add).
            more_stars = (STAR,) * (path_len - glob_len + 1)
            ss_glob = glob[:ss] + more_stars + glob[ss + 1:]
        elif path_len == glob_len - 1:
            # Glob has one more segment than the path. Here we remove
            # the '**' segment altogether to match the lengths up.
            ss_glob = glob[:ss] + glob[ss + 1:]

    # If we were successful in matching up the lengths, then we can
    # compare them using fnmatch.
    if path_len == len(ss_glob):
        for (s, g) in zip(map(int_str, segments), map(int_str, ss_glob)):
            # Match the stars we added to the glob to the type of the
            # segment itself.
            if g is STAR:
                if isinstance(s, bytes):
                    g = b'*'
                else:
                    g = u'*'

            # Let's see if the glob matches. We will turn any kind of
            # exception while attempting to match into a False for the
            # match.
            try:
                if not fnmatchcase(s, g):
                    return False
            except:
                return False

        # All of the segments matched so we have a complete match.
        return True

    # Otherwise the lengths aren't the same and we couldn't have a
    # match.
    return False


def extend(thing, index, value=None):
    '''
    Extend a sequence like thing such that it contains at least index +
    1 many elements. The extension values will be None (default).

    extend(thing, int) -> [thing..., None, ...]
    '''
    try:
        expansion = (type(thing)())

        # Using this rather than the multiply notation in order to support a
        # wider variety of sequence like things.
        extra = (index + 1) - len(thing)
        for i in range(extra):
            expansion += [value]
        thing.extend(expansion)
    except TypeError:
        # We attempted to extend something that doesn't support it. In
        # this case we assume thing is actually more like a dictionary
        # and doesn't need to be extended.
        pass

    return thing


def __default_creator__(current, segments, i, hints=()):
    '''
    Create missing path components. If the segment is an int, then it will
    create a list. Otherwise a dictionary is created.

    set(obj, segments, value) -> obj
    '''
    segment = segments[i]
    length = len(segments)

    if isinstance(segment, int):
        extend(current, segment)

    # Infer the type from the hints provided.
    if i < len(hints):
        current[segment] = hints[i][1]()
    else:
        # Peek at the next segment to determine if we should be
        # creating an array for it to access or dictionary.
        if i + 1 < length:
            segment_next = segments[i + 1]
        else:
            segment_next = None

        if isinstance(segment_next, int):
            current[segment] = []
        else:
            current[segment] = {}


def set(obj, segments, value, creator=__default_creator__, hints=()):
    '''
    Set the value in obj at the place indicated by segments. If creator is not
    None (default __default_creator__), then call the creator function to
    create any missing path components.

    set(obj, segments, value) -> obj
    '''
    current = obj
    length = len(segments)

    # For everything except the last value, walk down the path and
    # create if creator is set.
    for (i, segment) in enumerate(segments[:-1]):
        try:
            # Optimistically try to get the next value. This makes the
            # code agnostic to whether current is a list or a dict.
            # Unfortunately, for our use, 'x in thing' for lists checks
            # values, not keys whereas dicts check keys.
            current[segment]
        except:
            if creator is not None:
                creator(current, segments, i, hints=hints)
            else:
                raise

        current = current[segment]
        if i != length - 1 and leaf(current):
            raise PathNotFound('Path: {}[{}]'.format(segments, i))

    if isinstance(segments[-1], int):
        extend(current, segments[-1])

    current[segments[-1]] = value

    return obj


def fold(obj, f, acc):
    '''
    Walk obj applying f to each path and returning accumulator acc.

    The function f will be called, for each result in walk(obj):

        f(obj, (segments, value), acc)

    If the function f returns False (exactly False), then processing
    will stop. Otherwise processing will continue with the next value
    retrieved from the walk.

    fold(obj, f(obj, (segments, value), acc) -> bool, acc) -> acc
    '''
    for pair in walk(obj):
        if f(obj, pair, acc) is False:
            break
    return acc


def foldm(obj, f, acc):
    '''
    Same as fold(), but permits mutating obj.

    This requires all paths in walk(obj) to be loaded into memory
    (whereas fold does not).

    foldm(obj, f(obj, (segments, value), acc) -> bool, acc) -> acc
    '''
    pairs = tuple(walk(obj))
    for pair in pairs:
        (segments, value) = pair
        if f(obj, pair, acc) is False:
            break
    return acc


def view(obj, glob):
    '''
    Return a view of the object where the glob matches. A view retains
    the same form as the obj, but is limited to only the paths that
    matched. Views are new objects (a deepcopy of the matching values).

    view(obj, glob) -> obj'
    '''
    def f(obj, pair, result):
        (segments, value) = pair
        if match(segments, glob):
            if not has(result, segments):
                set(result, segments, deepcopy(value), hints=types(obj, segments))
    return fold(obj, f, type(obj)())
