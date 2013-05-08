class InvalidGlob(Exception):
    """The glob passed is invalid."""
    pass

class PathNotFound(Exception):
    """One or more elements of the requested path did not exist in the object"""
    pass
