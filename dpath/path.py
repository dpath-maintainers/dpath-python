import dpath.exceptions
import re
import fnmatch
import shlex

def paths(obj, dirs=True, leaves=True, path=[], skip=False):
    """Yield all paths of the object.

    Arguments:

    obj -- An object to get paths from.

    Keyword Arguments:

    dirs -- Yield intermediate paths.
    leaves -- Yield the paths with leaf objects.
    path -- A list of keys representing the path.
    skip -- Skip special keys beginning with '+'.

    """
    if isinstance(obj, dict):
        for (i, v) in enumerate(obj):
            if skip and v[0] == '+':
                continue
            newpath = path + [v]
            if dirs:
                yield newpath
            for child in paths(obj[v], dirs, leaves, newpath, skip):
                yield child
    elif isinstance(obj, (list, tuple)):
        for (i, v) in enumerate(obj):
            newpath = path + [i]
            if dirs:
                yield newpath
            for child in paths(obj[i], dirs, leaves, newpath, skip):
                yield child
    elif leaves:
        yield path + [obj]
    elif not dirs:
        yield path

def match(path, glob):
    """Match the path with the glob.

    Arguments:

    path -- A list of keys representing the path.
    glob -- A list of globs to match against the path.

    """
    path_len = len(path)
    glob_len = len(glob)

    ss = -1
    ss_glob = glob
    if '**' in glob:
        ss = glob.index('**')
        if '**' in glob[ss + 1:]:
            raise dpath.exceptions.InvalidGlob("Invalid glob. Only one '**' is permitted per glob.")

        if path_len >= glob_len:
            # Just right or more stars.
            more_stars = ['*'] * (path_len - glob_len + 1)
            ss_glob = glob[:ss] + more_stars + glob[ss + 1:]
        elif path_len == glob_len - 1:
            # Need one less star.
            ss_glob = glob[:ss] + glob[ss + 1:]

    if path_len == len(ss_glob):
        return all(map(fnmatch.fnmatch, map(str, path), map(str, ss_glob)))

    return False

def search(obj, glob, dirs=True, leaves=False):
    """Search the object paths that match the glob."""
    for path in paths(obj, dirs, leaves, skip=True):
        if match(path, glob):
            yield path

def is_glob(string):
    return any([c in string for c in '*?[]!'])

def set(obj, path, value, create_missing=True):
    """Set the value of the given path in the object. Path
    must be a list of specific path elements, not a glob.

    If create_missing is True (the default behavior), then any
    missing path components in the dictionary are made silently.
    Otherwise, if False, an exception is thrown if path
    components are missing.
    """
    cur = obj
    traversed = []
    for elem in path:
        if (not elem in obj) and (create_missing):
            if len(traversed) == len(path):
                obj[elem] = value
                return
            obj[elem] = {}
        else:
            raise dpath.exceptions.PathNotFound(
                "{} does not exist in {}".format(
                    elem,
                    "/".join(traversed)
                    )
                )
        traversed.append(elem)
        obj = obj[elem]

def get(obj, path, view=False):
    """Get the value of the given path.

    Arguments:

    obj -- Object to look in.
    path -- A list of keys representing the path.

    Keyword Arguments:

    view -- Return a view of the object.

    """
    target = obj
    head = type(target)()
    tail = head
    up = None
    for key in path:
        target = target[key]
        if view:
            if isinstance(tail, dict):
                if target == None:
                    tail[key] = None
                else:
                    tail[key] = type(target)()
            elif isinstance(tail, list):
                if key >= len(tail):
                    tail += [None] * (key - len(tail) + 1)
                if target == None:
                    tail[key] = None
                else:
                    tail[key] = type(target)()
            up = tail
            tail = tail[key]
    if view:
        up[path[-1]] = target
        return head
    else:
        if isinstance(target, basestring):
            target = '"' + target + '"'
        return target
