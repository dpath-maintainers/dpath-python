from nose.tools import assert_raises
import dpath.util
import mock


def test_util_get_root():
    x = {'p': {'a': {'t': {'h': 'value'}}}}

    ret = dpath.util.get(x, '/p/a/t/h')
    assert(ret == 'value')

    ret = dpath.util.get(x, '/')
    assert(ret == x)


def test_get_explicit_single():
    ehash = {
        "a": {
            "b": {
                "c": {
                    "d": 0,
                    "e": 1,
                    "f": 2,
                },
            },
        },
    }

    assert(dpath.util.get(ehash, '/a/b/c/f') == 2)
    assert(dpath.util.get(ehash, ['a', 'b', 'c', 'f']) == 2)
    assert(dpath.util.get(ehash, ['a', 'b', 'c', 'f'], default=5) == 2)
    assert(dpath.util.get(ehash, ['does', 'not', 'exist'], default=None) is None)
    assert(dpath.util.get(ehash, ['doesnt', 'exist'], default=5) == 5)


def test_get_glob_single():
    ehash = {
        "a": {
            "b": {
                "c": {
                    "d": 0,
                    "e": 1,
                    "f": 2,
                },
            },
        },
    }

    assert(dpath.util.get(ehash, '/a/b/*/f') == 2)
    assert(dpath.util.get(ehash, ['a', 'b', '*', 'f']) == 2)
    assert(dpath.util.get(ehash, ['a', 'b', '*', 'f'], default=5) == 2)
    assert(dpath.util.get(ehash, ['doesnt', '*', 'exist'], default=6) == 6)


def test_get_glob_multiple():
    ehash = {
        "a": {
            "b": {
                "c": {
                    "d": 0,
                },
                "e": {
                    "d": 0,
                },
            },
        },
    }

    assert_raises(ValueError, dpath.util.get, ehash, '/a/b/*/d')
    assert_raises(ValueError, dpath.util.get, ehash, ['a', 'b', '*', 'd'])
    assert_raises(ValueError, dpath.util.get, ehash, ['a', 'b', '*', 'd'], default=3)


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
                    "f": 2,
                },
            },
        },
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
    searchfunc.assert_called_with({}, '/a/b', True, ':', y, False)

    dpath.util.values({}, ['a', 'b'], ':', y, False)
    searchfunc.assert_called_with({}, ['a', 'b'], True, ':', y, False)


def test_none_values():
    d = {'p': {'a': {'t': {'h': None}}}}

    v = dpath.util.get(d, 'p/a/t/h')
    assert(v is None)


def test_values_list():
    a = {
        'actions': [
            {
                'type': 'correct',
            },
            {
                'type': 'incorrect',
            },
        ],
    }

    ret = dpath.util.values(a, 'actions/*')
    assert(isinstance(ret, list))
    assert(len(ret) == 2)
