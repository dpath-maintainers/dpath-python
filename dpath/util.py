import dpath.path
import dpath.exceptions

MERGE_REPLACE=(1 << 1)
MERGE_ADDITIVE=(1 << 2)
MERGE_TYPESAFE=(1 << 3)

def new(obj, path, value, separator="/"):
    """
    Set the element at the terminus of path to value, and create
    it if it does not exist (as opposed to 'set' that can only
    change existing keys).

    path will NOT be treated like a glob. If it has globbing
    characters in it, they will become part of the resulting
    keys
    """
    pathobj = dpath.path.path_types(obj, path.lstrip(separator).split(separator))
    return dpath.path.set(obj, pathobj, value, create_missing=True)

def delete(obj, glob, separator="/", afilter=None):
    """
    Given a path glob, delete all elements that match the glob.

    Returns the number of deleted objects. Raises PathNotFound if no paths are
    found to delete.
    """
    deleted = 0
    paths = []
    for path in _inner_search(obj, glob.lstrip(separator).split(separator), separator):
        # These are yielded back, don't mess up the dict.
        paths.append(path)

    for path in paths:
        cur = obj
        prev = None
        for item in path:
            prev = cur
            try:
                cur = cur[item[0]]
            except AttributeError as e:
                # This only happens when we delete X/Y and the next
                # item in the paths is X/Y/Z
                pass
        if (not afilter) or (afilter and afilter(prev[item[0]])):
            prev.pop(item[0])
        deleted += 1
    if not deleted:
        raise dpath.exceptions.PathNotFound("Could not find {} to delete it".format(glob))
    return deleted

def set(obj, glob, value, separator="/", afilter=None):
    """
    Given a path glob, set all existing elements in the document
    to the given value. Returns the number of elements changed.
    """
    changed = 0
    for path in _inner_search(obj, glob.lstrip(separator).split(separator), separator):
        changed += 1
        dpath.path.set(obj, path, value, create_missing=False, afilter=afilter)
    return changed

def search(obj, glob, yielded=False, separator="/", afilter=None, dirs = True):
    """
    Given a path glob, return a dictionary containing all keys
    that matched the given glob.

    If 'yielded' is true, then a dictionary will not be returned.
    Instead tuples will be yielded in the form of (path, value) for
    every element in the document that matched the glob.
    """

    def _search_view(obj, glob, separator, afilter, dirs):
        view = {}
        for path in _inner_search(obj, glob.lstrip(separator).split(separator), separator, dirs=dirs):
            try:
                val = dpath.path.get(obj, path, afilter=afilter, view=True)
                merge(view, val)
            except dpath.exceptions.FilteredValue:
                pass
        return view

    def _search_yielded(obj, glob, separator, afilter, dirs):
        for path in _inner_search(obj, glob.lstrip(separator).split(separator), separator, dirs=dirs):
            try:
                val = dpath.path.get(obj, path, view=False, afilter=afilter)
                yield (separator.join(map(str, dpath.path.paths_only(path))), val)
            except dpath.exceptions.FilteredValue:
                pass

    if afilter is not None:
        dirs = False
    if yielded:
        return _search_yielded(obj, glob, separator, afilter, dirs)
    return _search_view(obj, glob, separator, afilter, dirs)

def _inner_search(obj, glob, separator, dirs=True, leaves=False):
    """Search the object paths that match the glob."""
    for path in dpath.path.paths(obj, dirs, leaves, skip=True, separator = separator):
        if dpath.path.match(path, glob):
            yield path

def merge(dst, src, separator="/", afilter=None, flags=MERGE_ADDITIVE, _path=""):
    """Merge source into destination. Like dict.update() but performs
    deep merging.

    flags is an OR'ed combination of MERGE_ADDITIVE, MERGE_REPLACE, or
    MERGE_TYPESAFE.
        * MERGE_ADDITIVE : List objects are combined onto one long
          list (NOT a set). This is the default flag.
        * MERGE_REPLACE : Instead of combining list objects, when
          2 list objects are at an equal depth of merge, replace
          the destination with the source.
        * MERGE_TYPESAFE : When 2 keys at equal levels are of different
          types, raise a TypeError exception. By default, the source
          replaces the destination in this situation.
    """

    if afilter:
        # Having merge do its own afiltering is dumb, let search do the
        # heavy lifting for us.
        src = search(src, '**', afilter=afilter)
        return merge(dst, src)

    def _check_typesafe(obj1, obj2, key, path):
        if not key in obj1:
            return
        elif ( (flags & MERGE_TYPESAFE == MERGE_TYPESAFE) and (type(obj1[key]) != type(obj2[key]))):
            raise TypeError("Cannot merge objects of type {} and {} at {}"
                            "".format(type(obj1[key]), type(obj2[key]), path))
        elif ( (flags & MERGE_TYPESAFE != MERGE_TYPESAFE) and (type(obj1[key]) != type(obj2[key]))):
            obj1.pop(key)

    if isinstance(src, dict):
        for (i, v) in enumerate(src):
            _check_typesafe(dst, src, v, separator.join([_path, str(v)]))

            if not v in dst:
                dst[v] = src[v]
            else:
                if not isinstance(src[v], (dict, list)):
                    dst[v] = src[v]
                else:
                    merge(dst[v], src[v], afilter=afilter, flags=flags,
                          _path=separator.join([_path, str(v)]), separator=separator)
    elif isinstance(src, list):
        for (i, v) in enumerate(src):
            _check_typesafe(dst, src, i, separator.join([_path, str(i)]))
            dsti = i
            if ( flags & MERGE_ADDITIVE):
                dsti = len(dst)
            if dsti >= len(dst):
                dst += [None] * (dsti - (len(dst) - 1))
            if dst[dsti] == None:
                dst[dsti] = src[i]
            else:
                if not isinstance(src[i], (dict, list)):
                    dst[dsti] = src[i]
                else:
                    merge(dst[i], src[i], afilter=afilter, flags=flags,
                          _path=separator.join([_path, str(i)]), separator=separator)
