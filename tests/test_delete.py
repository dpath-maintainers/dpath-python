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
        "other": {
            "d": 31,
        },
    }

    assert dpath.delete(dict, '/a/*', afilter=afilter) == 1
    assert dict['a']['b'] == 0
    assert dict['a']['c'] == 1
    assert 'd' not in dict['a']
    assert dict['other'] == {'d': 31}


def test_delete_filter_missing_glob():
    dict = {'other': 31}

    with helper.assertRaises(dpath.exceptions.PathNotFound):
        dpath.delete(dict, '/missing/*', afilter=lambda value: value == 31)

    assert dict == {'other': 31}


def test_delete_filter_rejects_matching_values():
    dict = {'a': 0, 'other': 31}

    with helper.assertRaises(dpath.exceptions.PathNotFound):
        dpath.delete(dict, '/a', afilter=lambda value: value == 31)

    assert dict == {'a': 0, 'other': 31}


def test_delete_filter_list_glob():
    dict = {'a': [31, 0, 31], 'other': [31, 31]}

    assert dpath.delete(dict, ['a', '*'], afilter=lambda value: value == 31) == 2
    assert dict == {'a': [None, 0], 'other': [31, 31]}


def test_delete_filter_recursive_glob():
    dict = {'a': {'remove': 31, 'keep': 31}, 'b': {'c': {'remove': 0}}}

    assert dpath.delete(dict, '**;remove', separator=';', afilter=lambda value: value == 31) == 1
    assert dict == {'a': {'keep': 31}, 'b': {'c': {'remove': 0}}}
