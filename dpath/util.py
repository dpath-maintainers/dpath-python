import dpath.path

def new(obj, path, value):
    """
    Set the element at the terminus of path to value, and create
    it if it does not exist (as opposed to 'set' that can only
    change existing keys).

    path will NOT be treated like a glob. If it has globbing
    characters in it, they will become part of the resulting
    keys
    """
    return dpath.path.set(obj, path.split("/"), value, create_missing=True)

def set(obj, glob, value):
    """
    Given a path glob, set all existing elements in the document
    to the given value. Returns the number of elements changed.
    """
    changed = 0
    for path in dpath.path.search(obj, glob.split("/")):
        changed += 1
        dpath.path.set(obj, path, value, create_missing=False)
    return changed

def search(obj, glob, yielded=False):
    """
    Given a path glob, return a dictionary containing all keys
    that matched the given glob.

    If 'yielded' is true, then a dictionary will not be returned.
    Instead tuples will be yielded in the form of (path, value) for
    every element in the document that matched the glob.
    """

    def _search_view(obj, glob):
        view = {}
        for path in dpath.path.search(obj, glob.split("/")):
            dpath.path.merge(view, dpath.path.get(obj, path, view=True))
        return view

    def _search_yielded(obj, glob):
        for path in dpath.path.search(obj, glob.split("/")):
            yield ("/".join(path), dpath.path.get(obj, path))

    if yielded:
        return _search_yielded(obj, glob)
    return _search_view(obj, glob)

def merge(dst, src):
    """Merge source into destination. Like dict.update() but performs
    deep merging."""
    if isinstance(src, dict):
        for (i, v) in enumerate(src):
            if not v in dst:
                dst[v] = src[v]
            else:
                if not isinstance(src[v], (dict, list)):
                    dst[v] = src[v]
                else:
                    merge(dst[v], src[v])
    elif isinstance(src, list):
        for (i, v) in enumerate(src):
            if i >= len(dst):
                dst += [None] * (i - len(dst) + 1)
            if dst[i] == None:
                dst[i] = src[i]
            else:
                if not isinstance(src[i], (dict, list)):
                    dst[i] = src[i]
                else:
                    merge(dst[i], src[i])

