import nose
from nose.tools import assert_raises
import dpath.util
import mock

def test_get_explicit_single():
    ehash = {
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
    assert(dpath.util.get(ehash, '/a/b/c/f') == 2)
    assert(dpath.util.get(ehash, ['a', 'b', 'c', 'f']) == 2)

def test_get_glob_single():
    ehash = {
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
    assert(dpath.util.get(ehash, '/a/b/*/f') == 2)
    assert(dpath.util.get(ehash, ['a', 'b', '*', 'f']) == 2)

def test_get_glob_multiple():
    ehash = {
        "a": {
            "b": {
                "c": {
                    "d": 0
                },
                "e": {
                    "d": 0
                }
            }
        }
    }
    assert_raises(ValueError, dpath.util.get, ehash, '/a/b/*/d')
    assert_raises(ValueError, dpath.util.get, ehash, ['a', 'b', '*', 'd'])

def test_get_absent():
    ehash = {}
    assert_raises(KeyError, dpath.util.get, ehash, '/a/b/c/d/f')
    assert_raises(KeyError, dpath.util.get, ehash, ['a', 'b', 'c', 'd', 'f'])

def test_values():
    ehash = {
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
    ret = dpath.util.values(ehash, '/a/b/c/*')
    assert(isinstance(ret, list))
    assert(0 in ret)
    assert(1 in ret)
    assert(2 in ret)

    ret = dpath.util.values(ehash, ['a', 'b', 'c', '*'])
    assert(isinstance(ret, list))
    assert(0 in ret)
    assert(1 in ret)
    assert(2 in ret)

@mock.patch('dpath.util.search')
def test_values_passes_through(searchfunc):
    searchfunc.return_value = []
    def y():
        pass
    dpath.util.values({}, '/a/b', ':', y, False)
    searchfunc.assert_called_with({}, '/a/b', dirs=False, yielded=True, separator=':', afilter=y)
    dpath.util.values({}, ['a', 'b'], ':', y, False)
    searchfunc.assert_called_with({}, ['a', 'b'], dirs=False, yielded=True, separator=':', afilter=y)
