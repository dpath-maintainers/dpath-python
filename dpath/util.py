import dpath.path

def search(obj, glob, yielded=False):
    """
    Given a path glob, return a dictionary containing all keys
    that matched the given glob.

    If 'yielded' is true, then a dictionary will not be returned.
    Instead tuples will be yielded in the form of (path, value) for
    every element in the document that matched the glob. The path
    will be a list of separated path elements constructing the path.
    ("/".join() them again if that's what you want.)
    """
    if yielded:
        return _search_yielded(obj, glob)
    return _search_view(obj, glob)
def _search_view(obj, glob):
    view = {}
    for path in dpath.path.search(obj, glob.split("/")):
        dpath.path.merge(view, dpath.path.get(obj, path, view=True))
    return view

def _search_yielded(obj, glob):
    for path in dpath.path.search(obj, glob.split("/")):
        yield (path, dpath.path.get(obj, path))

def merge(dst, src):
    """Merge source into destination. Like dict.copy() but performs
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

