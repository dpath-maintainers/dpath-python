import nose
import dpath.util

def test_search_paths_with_separator():
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
        'a;b',
        'a;b;c',
        'a;b;c;d',
        'a;b;c;e',
        'a;b;c;f'
        ]
    for (path, value) in dpath.util.search(dict, '/**', yielded=True, separator=";"):
        assert(path in paths)

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
    for (path, value) in dpath.util.search(dict, '/**', yielded=True):
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
    for (path, value) in dpath.util.search(dict, '/**', yielded=True, filter=filter):
        print path
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
    for (path, value) in dpath.util.search(dict, '/a/**/[df]', yielded=True):
        assert(path in paths)

def test_search_return_dict_head():
    tdict = {
        "a": {
            "b": {
                0: 0,
                1: 1,
                2: 2}
            }
        }
    res = dpath.util.search(tdict, '/a/b')
    print res
    assert(isinstance(res['a']['b'], dict))
    assert(len(res['a']['b']) == 3)
    assert(res['a']['b'] == {0: 0, 1: 1, 2: 2})

def test_search_return_dict_globbed():
    tdict = {
        "a": {
            "b": {
                0: 0,
                1: 1,
                2: 2}
            }
        }
    res = dpath.util.search(tdict, '/a/b/[02]')
    assert(isinstance(res['a']['b'], dict))
    assert(len(res['a']['b']) == 2)
    assert(res['a']['b'] == {0: 0, 2: 2})

def test_search_return_list_head():
    tdict = {
        "a": {
            "b": [
                0,
                1,
                2]
            }
        }
    res = dpath.util.search(tdict, '/a/b')
    assert(isinstance(res['a']['b'], list))
    assert(len(res['a']['b']) == 3)
    assert(res['a']['b'] == [0, 1, 2])

def test_search_return_list_globbed():
    tdict = {
        "a": {
            "b": [
                0,
                1,
                2]
            }
        }
    res = dpath.util.search(tdict, '/a/b/[02]')
    assert(isinstance(res['a']['b'], list))
    assert(len(res['a']['b']) == 2)
    assert(res['a']['b'] == [0, 2])

