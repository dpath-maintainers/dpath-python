from nose2.tools.such import helper

import dpath
import dpath.exceptions


def test_delete_separator():
    dict = {
        "a": {
            "b": 0,
        },
    }

    dpath.delete(dict, ';a;b', separator=";")
    assert 'b' not in dict['a']


def test_delete_existing():
    dict = {
        "a": {
            "b": 0,
        },
    }

    dpath.delete(dict, '/a/b')
    assert 'b' not in dict['a']


def test_delete_missing():
    dict = {
        "a": {
        },
    }

    with helper.assertRaises(dpath.exceptions.PathNotFound):
        dpath.delete(dict, '/a/b')


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

    dpath.delete(dict, '/a/*', afilter=afilter)
    assert dict['a']['b'] == 0
    assert dict['a']['c'] == 1
    assert 'd' not in dict['a']


def test_delete_all_list_elements():
    data = {'items': [0, 1, 2]}

    assert dpath.delete(data, 'items/*') == 3
    assert data == {'items': []}


def test_delete_list_suffix():
    data = {'items': [0, 1, 2]}

    assert dpath.delete(data, 'items/[12]') == 2
    assert data == {'items': [0]}


def test_delete_nested_list_elements():
    data = {'items': [[0, 1], [2, 3]]}

    assert dpath.delete(data, 'items/*/*') == 4
    assert data == {'items': [[], []]}


def test_delete_interior_list_element_keeps_indices():
    data = {'items': [0, 1, 2]}

    assert dpath.delete(data, 'items/1') == 1
    assert data == {'items': [0, None, 2]}


def test_delete_list_suffix_keeps_original_none():
    data = {'items': [None, 1, 2]}

    assert dpath.delete(data, 'items/[12]') == 2
    assert data == {'items': [None]}
