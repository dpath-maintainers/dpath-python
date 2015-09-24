import sys
if sys.version_info < (3,):
    def u(x):
        x = x if isinstance(x, basestring) else str(x)
        return try_decode(x)
else:
    def u(x):
        return str(x)

def try_decode(obj):
    """
    Tries to decode a basestring (python 2/3) into a unicode string.
    Returns the OBJ if it fails or if it isn't a basestring. Otherwise returns the unicode version of the
    base string.
    """
    try:
        if isinstance(obj, basestring):
            return obj.decode('utf-8')
        else:
            return obj
    except Exception:
        return obj

def get_subpath(parent_path, child_element, separator):
    """
    Returns the new path of CHILD_ELEMENT to search given a PARENT_PATH
    """
    return separator.join([parent_path, u(try_decode(child_element))])
