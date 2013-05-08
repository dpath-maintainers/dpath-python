import dpath.path

def

def search(obj, glob, yielded=False):
    """
    Given a path glob, return a dictionary containing all keys
    that matched the given glob.

    If 'yielded' is true, then a dictionary will not be returned.
    Instead tuples will be yielded in the form of (path, value) for
    every element in the document that matched the glob.
    """
    dpath.path.search(obj, glob.split("/"))

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

