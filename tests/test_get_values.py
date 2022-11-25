import datetime
import decimal
import time

import mock
from nose2.tools.such import helper

import dpath


def test_util_get_root():
    x = {'p': {'a': {'t': {'h': 'value'}}}}

    ret = dpath.get(x, '/p/a/t/h')
    assert ret == 'value'

    ret = dpath.get(x, '/')
    assert ret == x


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

    assert dpath.get(ehash, '/a/b/c/f') == 2
    assert dpath.get(ehash, ['a', 'b', 'c', 'f']) == 2
    assert dpath.get(ehash, ['a', 'b', 'c', 'f'], default=5) == 2
    assert dpath.get(ehash, ['does', 'not', 'exist'], default=None) is None
    assert dpath.get(ehash, ['doesnt', 'exist'], default=5) == 5


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

    assert dpath.get(ehash, '/a/b/*/f') == 2
    assert dpath.get(ehash, ['a', 'b', '*', 'f']) == 2
    assert dpath.get(ehash, ['a', 'b', '*', 'f'], default=5) == 2
    assert dpath.get(ehash, ['doesnt', '*', 'exist'], default=6) == 6


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

    helper.assertRaises(ValueError, dpath.get, ehash, '/a/b/*/d')
    helper.assertRaises(ValueError, dpath.get, ehash, ['a', 'b', '*', 'd'])
    helper.assertRaises(ValueError, dpath.get, ehash, ['a', 'b', '*', 'd'], default=3)


def test_get_absent():
    ehash = {}

    helper.assertRaises(KeyError, dpath.get, ehash, '/a/b/c/d/f')
    helper.assertRaises(KeyError, dpath.get, ehash, ['a', 'b', 'c', 'd', 'f'])


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

    ret = dpath.values(ehash, '/a/b/c/*')
    assert isinstance(ret, list)
    assert 0 in ret
    assert 1 in ret
    assert 2 in ret

    ret = dpath.values(ehash, ['a', 'b', 'c', '*'])
    assert isinstance(ret, list)
    assert 0 in ret
    assert 1 in ret
    assert 2 in ret


@mock.patch('dpath.search')
def test_values_passes_through(searchfunc):
    searchfunc.return_value = []

    def y():
        return False

    dpath.values({}, '/a/b', ':', y, False)
    searchfunc.assert_called_with({}, '/a/b', True, ':', y, False)

    dpath.values({}, ['a', 'b'], ':', y, False)
    searchfunc.assert_called_with({}, ['a', 'b'], True, ':', y, False)


def test_none_values():
    d = {'p': {'a': {'t': {'h': None}}}}

    v = dpath.get(d, 'p/a/t/h')
    assert v is None


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

    ret = dpath.values(a, 'actions/*')
    assert isinstance(ret, list)
    assert len(ret) == 2


def test_non_leaf_leaf():
    # The leaves in this test aren't leaf(thing) == True, but we should still
    # be able to get them. They should also not prevent fetching other values.

    def func(x):
        return x

    testdict = {
        'a': func,
        'b': lambda x: x,
        'c': [
            {
                'a',
                'b',
            },
        ],
        'd': [
            decimal.Decimal(1.5),
            decimal.Decimal(2.25),
        ],
        'e': datetime.datetime(2020, 1, 1),
        'f': {
            'config': 'something',
        },
    }

    # It should be possible to get the callables:
    assert dpath.get(testdict, 'a') == func
    assert dpath.get(testdict, 'b')(42) == 42

    # It should be possible to get other values:
    assert dpath.get(testdict, 'c/0') == testdict['c'][0]
    assert dpath.get(testdict, 'd')[0] == testdict['d'][0]
    assert dpath.get(testdict, 'd/0') == testdict['d'][0]
    assert dpath.get(testdict, 'd/1') == testdict['d'][1]
    assert dpath.get(testdict, 'e') == testdict['e']

    # Values should also still work:
    assert dpath.values(testdict, 'f/config') == ['something']

    # Data classes should also be retrievable:
    try:
        import dataclasses
    except:
        return

    @dataclasses.dataclass
    class Connection:
        group_name: str
        channel_name: str
        last_seen: float

    testdict['g'] = {
        'my-key': Connection(
            group_name='foo',
            channel_name='bar',
            last_seen=time.time(),
        ),
    }

    assert dpath.search(testdict, 'g/my*')['g']['my-key'] == testdict['g']['my-key']
