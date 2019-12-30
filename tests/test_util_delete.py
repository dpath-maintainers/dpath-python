from nose.tools import raises
import dpath.util
import dpath.exceptions


def test_delete_separator():
    dict = {
        "a": {
            "b": 0,
        },
    }

    dpath.util.delete(dict, ';a;b', separator=";")
    assert('b' not in dict['a'])


def test_delete_existing():
    dict = {
        "a": {
            "b": 0,
        },
    }

    dpath.util.delete(dict, '/a/b')
    assert('b' not in dict['a'])


@raises(dpath.exceptions.PathNotFound)
def test_delete_missing():
    dict = {
        "a": {
        },
    }

    dpath.util.delete(dict, '/a/b')


def test_delete_filter():
    def afilter(x):
        if int(x) == 31:
            return True
        return False

    dict = {
        "a": {
            "b": 0,
            "c": 1,
            "d": 31,
        },
    }

    dpath.util.delete(dict, '/a/*', afilter=afilter)
    assert (dict['a']['b'] == 0)
    assert (dict['a']['c'] == 1)
    assert ('d' not in dict['a'])
