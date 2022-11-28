from collections.abc import MutableSequence, MutableMapping

from nose2.tools.such import helper

import dpath
from dpath import MergeType


class TestMapping(MutableMapping):
    def __init__(self, data=None):
        if data is None:
            data = {}

        self._mapping = {}
        self._mapping.update(data)

    def __len__(self):
        return len(self._mapping)

    def __iter__(self):
        return iter(self._mapping)

    def __contains__(self, key):
        return key in self._mapping

    def __getitem__(self, key):
        return self._mapping[key]

    def __setitem__(self, key, value):
        self._mapping[key] = value

    def __delitem__(self, key):
        del self._mapping[key]


class TestSequence(MutableSequence):
    def __init__(self, data=None):
        if data is None:
            data = list()

        self._list = [] + data

    def __len__(self):
        return len(self._list)

    def __getitem__(self, idx):
        return self._list[idx]

    def __delitem__(self, idx):
        del self._list[idx]

    def __setitem__(self, idx, value):
        self._list[idx] = value

    def __str__(self):
        return str(self._list)

    def __eq__(self, other):
        return self._list == other._list

    def __ne__(self, other):
        return not self.__eq__(other)

    def insert(self, idx, value):
        self._list.insert(idx, value)

    def append(self, value):
        self.insert(len(self._list), value)


def test_types_set():
    data = TestMapping({"a": TestSequence([0])})

    dpath.set(data, '/a/0', 1)
    assert data['a'][0] == 1

    data['a'][0] = 0

    dpath.set(data, ['a', '0'], 1)
    assert data['a'][0] == 1


def test_types_get_list_of_dicts():
    tdict = TestMapping({
        "a": TestMapping({
            "b": TestSequence([
                {0: 0},
                {0: 1},
                {0: 2},
            ]),
        }),
    })

    res = dpath.segments.view(tdict, ['a', 'b', 0, 0])

    assert isinstance(res['a']['b'], TestSequence)
    assert len(res['a']['b']) == 1
    assert res['a']['b'][0][0] == 0


def test_types_merge_simple_list_replace():
    src = TestMapping({
        "list": TestSequence([7, 8, 9, 10])
    })
    dst = TestMapping({
        "list": TestSequence([0, 1, 2, 3])
    })

    dpath.merge(dst, src, flags=MergeType.REPLACE)
    assert dst["list"] == TestSequence([7, 8, 9, 10]), "%r != %r" % (dst["list"], TestSequence([7, 8, 9, 10]))


def test_types_get_absent():
    ehash = TestMapping()
    helper.assertRaises(KeyError, dpath.get, ehash, '/a/b/c/d/f')
    helper.assertRaises(KeyError, dpath.get, ehash, ['a', 'b', 'c', 'd', 'f'])


def test_types_get_glob_multiple():
    ehash = TestMapping({
        "a": TestMapping({
            "b": TestMapping({
                "c": TestMapping({
                    "d": 0,
                }),
                "e": TestMapping({
                    "d": 0,
                }),
            }),
        }),
    })

    helper.assertRaises(ValueError, dpath.get, ehash, '/a/b/*/d')
    helper.assertRaises(ValueError, dpath.get, ehash, ['a', 'b', '*', 'd'])


def test_delete_filter():
    def afilter(x):
        if int(x) == 31:
            return True
        return False

    data = TestMapping({
        "a": TestMapping({
            "b": 0,
            "c": 1,
            "d": 31,
        }),
    })

    dpath.delete(data, '/a/*', afilter=afilter)
    assert data['a']['b'] == 0
    assert data['a']['c'] == 1
    assert 'd' not in data['a']
