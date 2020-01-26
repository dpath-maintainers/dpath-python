import nose
import copy
from nose.tools import raises


import dpath.util


def test_merge_typesafe_and_separator():
    src = {
        "dict": {
            "integer": 0,
        },
    }
    dst = {
        "dict": {
            "integer": "3",
        },
    }

    try:
        dpath.util.merge(dst, src, flags=(dpath.util.MERGE_ADDITIVE | dpath.util.MERGE_TYPESAFE), separator=";")
    except TypeError as e:
        assert(str(e).endswith("dict;integer"))

        return
    raise Exception("MERGE_TYPESAFE failed to raise an exception when merging between str and int!")


def test_merge_simple_int():
    src = {
        "integer": 0,
    }
    dst = {
        "integer": 3,
    }

    dpath.util.merge(dst, src)
    nose.tools.eq_(dst["integer"], src["integer"])


def test_merge_simple_string():
    src = {
        "string": "lol I am a string",
    }
    dst = {
        "string": "lol I am a string",
    }

    dpath.util.merge(dst, src)
    nose.tools.eq_(dst["string"], src["string"])


def test_merge_simple_list_additive():
    src = {
        "list": [7, 8, 9, 10],
    }
    dst = {
        "list": [0, 1, 2, 3],
    }

    dpath.util.merge(dst, src, flags=dpath.util.MERGE_ADDITIVE)
    nose.tools.eq_(dst["list"], [0, 1, 2, 3, 7, 8, 9, 10])


def test_merge_simple_list_replace():
    src = {
        "list": [7, 8, 9, 10],
    }
    dst = {
        "list": [0, 1, 2, 3],
    }

    dpath.util.merge(dst, src, flags=dpath.util.MERGE_REPLACE)
    nose.tools.eq_(dst["list"], [7, 8, 9, 10])


def test_merge_simple_dict():
    src = {
        "dict": {
            "key": "WEHAW",
        },
    }
    dst = {
        "dict": {
            "key": "",
        },
    }

    dpath.util.merge(dst, src)
    nose.tools.eq_(dst["dict"]["key"], src["dict"]["key"])


def test_merge_filter():
    def afilter(x):
        if "rubber" not in str(x):
            return False
        return True

    src = {
        "key": "metal",
        "key2": "rubber",
        "otherdict": {
            "key3": "I shouldn't be here",
        },
    }
    dst = {}

    dpath.util.merge(dst, src, afilter=afilter)
    assert ("key2" in dst)
    assert ("key" not in dst)
    assert ("otherdict" not in dst)


@raises(TypeError)
def test_merge_typesafe():
    src = {
        "dict": {
        },
    }
    dst = {
        "dict": [
        ],
    }

    dpath.util.merge(dst, src, flags=dpath.util.MERGE_TYPESAFE)


@raises(TypeError)
def test_merge_mutables():
    class tcid(dict):
        pass

    class tcis(list):
        pass

    src = {
        "mm": {
            "a": "v1",
        },
        "ms": [
            0,
        ],
    }
    dst = {
        "mm": tcid([
            ("a", "v2"),
            ("casserole", "this should keep"),
        ]),
        "ms": tcis(['a', 'b', 'c']),
    }

    dpath.util.merge(dst, src)
    print(dst)
    assert(dst["mm"]["a"] == src["mm"]["a"])
    assert(dst['ms'][2] == 'c')
    assert("casserole" in dst["mm"])

    dpath.util.merge(dst, src, flags=dpath.util.MERGE_TYPESAFE)


def test_merge_replace_1():
    dct_a = {"a": {"b": [1, 2, 3]}}
    dct_b = {"a": {"b": [1]}}
    dpath.util.merge(dct_a, dct_b, flags=dpath.util.MERGE_REPLACE)
    assert(len(dct_a['a']['b']) == 1)


def test_merge_replace_2():
    d1 = {'a': [0, 1, 2]}
    d2 = {'a': ['a']}
    dpath.util.merge(d1, d2, flags=dpath.util.MERGE_REPLACE)
    assert(len(d1['a']) == 1)
    assert(d1['a'][0] == 'a')


def test_merge_list():
    src = {"l": [1]}
    p1 = {"l": [2], "v": 1}
    p2 = {"v": 2}

    dst1 = {}
    for d in [copy.deepcopy(src), copy.deepcopy(p1)]:
        dpath.util.merge(dst1, d)
    dst2 = {}
    for d in [copy.deepcopy(src), copy.deepcopy(p2)]:
        dpath.util.merge(dst2, d)
    assert dst1["l"] == [1, 2]
    assert dst2["l"] == [1]

    dst1 = {}
    for d in [src, p1]:
        dpath.util.merge(dst1, d)
    dst2 = {}
    for d in [src, p2]:
        dpath.util.merge(dst2, d)
    assert dst1["l"] == [1, 2]
    assert dst2["l"] == [1, 2]
