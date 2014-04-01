from dpath import PY3
import dpath.exceptions
import dpath.options
import re
import fnmatch
import shlex
import sys
import traceback

def path_types(obj, path):
    """
    Given a list of path name elements, return anew list of [name, type] path components, given the reference object.
    """
    result = []
    #for elem in path[:-1]:
    cur = obj
    for elem in path[:-1]:
        if ((issubclass(cur.__class__, dict) and elem in cur)):
            result.append([elem, cur[elem].__class__])
            cur = cur[elem]
        elif (issubclass(cur.__class__, (list, tuple)) and int(elem) < len(cur)):
            elem = int(elem)
            result.append([elem, cur[elem].__class__])
            cur = cur[elem]
        else:
            result.append([elem, dict])
    try:
        try:
            result.append([path[-1], cur[path[-1]].__class__])
        except TypeError:
            result.append([path[-1], cur[int(path[-1])].__class__])
    except (KeyError, IndexError):
        result.append([path[-1], path[-1].__class__])
    return result

def paths_only(path):
    """
    Return a list containing only the pathnames of the given path list, not the types.
    """
    l = []
    for p in path:
        l.append(p[0])
    return l

def validate(path, separator="/", regex=None):
    """
    Validate that all the keys in the given list of path components are valid, given that they do not contain the separator, and match any optional regex given.
    """
    validated = []
    for elem in path:
        key = elem[0]
        strkey = str(key)
        if (separator and (separator in strkey)):
            raise dpath.exceptions.InvalidKeyName("{} at {} contains the separator {}"
                                                  "".format(strkey,
                                                            separator.join(validated),
                                                            separator))
        elif (regex and (not regex.findall(strkey))):
            raise dpath.exceptions.InvalidKeyName("{} at {} does not match the expression {}"
                                                  "".format(strkey,
                                                            separator.join(validated),
                                                            regex.pattern))
        validated.append(strkey)

def paths(obj, dirs=True, leaves=True, path=[], skip=False, separator="/"):
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
        # Python 3 support
        if PY3:
            iteritems = obj.items()
            string_class = str
        else: # Default to PY2
            iteritems = obj.iteritems()
            string_class = basestring

        for (k, v) in iteritems:
            if issubclass(k.__class__, (string_class)):
                if (not k) and (not dpath.options.ALLOW_EMPTY_STRING_KEYS):
                    raise dpath.exceptions.InvalidKeyName("Empty string keys not allowed without "
                                                          "dpath.options.ALLOW_EMPTY_STRING_KEYS=True")
                elif (skip and k[0] == '+'):
                    continue
            newpath = path + [[k, v.__class__]]
            validate(newpath, separator=separator)
            if dirs:
                yield newpath
            for child in paths(v, dirs, leaves, newpath, skip, separator=separator):
                yield child
    elif isinstance(obj, (list, tuple)):
        for (i, v) in enumerate(obj):
            newpath = path + [[i, v.__class__]]
            if dirs:
                yield newpath
            for child in paths(obj[i], dirs, leaves, newpath, skip, separator=separator):
                yield child
    elif leaves:
        yield path + [[obj, obj.__class__]]
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
        # Python 3 support
        if PY3:
            return all(map(fnmatch.fnmatch, list(map(str, paths_only(path))), list(map(str, ss_glob))))
        else: # Default to Python 2
            return all(map(fnmatch.fnmatch, map(str, paths_only(path)), map(str, ss_glob)))

    return False

def is_glob(string):
    return any([c in string for c in '*?[]!'])

def set(obj, path, value, create_missing=True, separator="/", afilter=None):
    """Set the value of the given path in the object. Path
    must be a list of specific path elements, not a glob.
    You can use dpath.util.set for globs, but the paths must
    slready exist.

    If create_missing is True (the default behavior), then any
    missing path components in the dictionary are made silently.
    Otherwise, if False, an exception is thrown if path
    components are missing.
    """
    cur = obj
    traversed = []

    def _presence_test_dict(obj, elem):
        return (elem[0] in obj)

    def _create_missing_dict(obj, elem):
        obj[elem[0]] = elem[1]()

    def _presence_test_list(obj, elem):
        return (int(str(elem[0])) < len(obj))

    def _create_missing_list(obj, elem):
        idx = int(str(elem[0]))
        while (len(obj)-1) < idx:
            obj.append(None)

    def _accessor_dict(obj, elem):
        return obj[elem[0]]

    def _accessor_list(obj, elem):
        return obj[int(str(elem[0]))]

    def _assigner_dict(obj, elem, value):
        obj[elem[0]] = value

    def _assigner_list(obj, elem, value):
        obj[int(str(elem[0]))] = value

    elem = None
    for elem in path:
        elem_value = elem[0]
        elem_type = elem[1]

        tester = None
        creator = None
        accessor = None
        assigner = None
        if issubclass(obj.__class__, (dict)):
            tester = _presence_test_dict
            creator = _create_missing_dict
            accessor = _accessor_dict
            assigner = _assigner_dict
        elif issubclass(obj.__class__, (list, tuple)):
            if not str(elem_value).isdigit():
                raise TypeError("Can only create integer indexes in lists, "
                                "not {}, in {}".format(type(obj),
                                                       separator.join(traversed)
                                                       )
                                )
            tester = _presence_test_list
            creator = _create_missing_list
            accessor = _accessor_list
            assigner = _assigner_list
        else:
            raise TypeError("Unable to path into elements of type {} "
                            "at {}".format(obj, separator.join(traversed)))

        if (not tester(obj, elem)) and (create_missing):
            creator(obj, elem)
        elif (not tester(obj, elem)):
            raise dpath.exceptions.PathNotFound(
                "{} does not exist in {}".format(
                    elem,
                    separator.join(traversed)
                    )
                )
        traversed.append(elem_value)
        if len(traversed) < len(path):
            obj = accessor(obj, elem)

    if elem is None:
        return
    if (afilter and afilter(accessor(obj, elem))) or (not afilter):
        assigner(obj, elem, value)

def get(obj, path, view=False, afilter=None):
    """Get the value of the given path.

    Arguments:

    obj -- Object to look in.
    path -- A list of keys representing the path.

    Keyword Arguments:

    view -- Return a view of the object.

    """
    index = 0
    path_count = len(path) - 1
    target = obj
    head = type(target)()
    tail = head
    up = None
    for pair in path:
        key = pair[0]
        target = target[key]

        if view:
            if isinstance(tail, dict):
                if issubclass(pair[1], (list, dict)) and index != path_count:
                    tail[key] = pair[1]()
                else:
                    tail[key] = target
                up = tail
                tail = tail[key]
            elif issubclass(tail.__class__, (list, tuple)):
                if issubclass(pair[1], (list, tuple, dict)) and index != path_count:
                    tail.append(pair[1]())
                else:
                    tail.append(target)
                up = tail
                tail = tail[-1]

        if not issubclass(target.__class__, (list, dict)):
            if (afilter and (not afilter(target))):
                raise dpath.exceptions.FilteredValue

        index += 1

    if view:
        return head
    else:
        return target
