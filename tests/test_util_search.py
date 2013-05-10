import nose
import dpath.util

def test_search_paths():
    dict = {
        "a": {
            "b": {
                "c": {
                    "d": 0,
                    "e": 1,
                    "f": 2
                    }
                }
            }
        }
    paths = [
        'a',
        'a/b',
        'a/b/c',
        'a/b/c/d',
        'a/b/c/e',
        'a/b/c/f'
        ]
    for (path, value) in dpath.util.search(dict, '**', yielded=True):
        assert(path in paths)

def test_search_filter():
    def filter(x):
        if x in [1, 2]:
            return True
        return False

    dict = {
        "a": {
            "b": {
                "c": {
                    "d": 0,
                    "e": 1,
                    "f": 2
                    }
                }
            }
        }
    paths = [
        'a/b/c/e',
        'a/b/c/f'
        ]
    for (path, value) in dpath.util.search(dict, '**', yielded=True, filter=filter):
        assert(path in paths)

def test_search_globbing():
    dict = {
        "a": {
            "b": {
                "c": {
                    "d": 0,
                    "e": 1,
                    "f": 2
                    }
                }
            }
        }
    paths = [
        'a/b/c/d',
        'a/b/c/f'
        ]
    for (path, value) in dpath.util.search(dict, 'a/**/[df]', yielded=True):
        assert(path in paths)
