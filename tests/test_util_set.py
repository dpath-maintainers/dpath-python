from functools import partial

import dpath.util


def test_set_existing_separator():
    dict = {
        "a": {
            "b": 0,
        },
    }

    dpath.util.set(dict, ';a;b', 1, separator=";")
    assert(dict['a']['b'] == 1)

    dict['a']['b'] = 0
    dpath.util.set(dict, ['a', 'b'], 1, separator=";")
    assert(dict['a']['b'] == 1)


def test_set_existing_dict():
    dict = {
        "a": {
            "b": 0,
        },
    }

    dpath.util.set(dict, '/a/b', 1)
    assert(dict['a']['b'] == 1)

    dict['a']['b'] = 0
    dpath.util.set(dict, ['a', 'b'], 1)
    assert(dict['a']['b'] == 1)


def test_set_existing_dict_not_affected_by_update_dict_flag():
    dict = {
        "a": {
            "b": 0,
        },
    }

    dpath.util.set(dict, '/a/b', 1, update_dict=True)
    assert(dict['a']['b'] == 1)

    dict['a']['b'] = 0
    dpath.util.set(dict, ['a', 'b'], 1, update_dict=True)
    assert(dict['a']['b'] == 1)


def test_set_existing_list():
    dict = {
        "a": [
            0,
        ],
    }

    dpath.util.set(dict, '/a/0', 1)
    assert(dict['a'][0] == 1)

    dict['a'][0] = 0
    dpath.util.set(dict, ['a', '0'], 1)
    assert(dict['a'][0] == 1)


def test_set_filter():
    def afilter(x):
        if int(x) == 31:
            return True
        return False

    dict = {
        "a": {
            "b": 0,
            "c": 1,
            "d": 31,
        }
    }

    dpath.util.set(dict, '/a/*', 31337, afilter=afilter)
    assert (dict['a']['b'] == 0)
    assert (dict['a']['c'] == 1)
    assert (dict['a']['d'] == 31337)

    dict = {
        "a": {
            "b": 0,
            "c": 1,
            "d": 31,
        }
    }

    dpath.util.set(dict, ['a', '*'], 31337, afilter=afilter)
    assert (dict['a']['b'] == 0)
    assert (dict['a']['c'] == 1)
    assert (dict['a']['d'] == 31337)


def test_set_filter_not_only_leaves():
    def afilter(key, value, x):
        return isinstance(x, dict) and x.get(key) == value

    dict_obj = {
        "a": {
            "b": {
                "name": "value",
                "b_nested": {
                    "name": "value",
                },
            },
            "c": 1,
            "d": 31,
        }
    }
    new_value = "new_value"

    dpath.util.set(dict_obj, '/a/b/*', new_value, afilter=partial(afilter, "name", "value"), only_leaves=False)

    assert dict_obj["a"]["b"]["b_nested"] == new_value

    dict_obj = {
        "a": {
            "b": {
                "name": "value",
                "b_nested": {
                    "name": "value",
                },
            },
            "c": 1,
            "d": 31,
        }
    }
    new_value = "new_value"

    dpath.util.set(dict_obj, ["a", "*"], new_value, afilter=partial(afilter, "name", "value"), only_leaves=False)

    assert dict_obj["a"]["b"] == new_value


def test_set_filter_not_only_leaves_and_update_dict_flag():
    def afilter(key, value, x):
        return isinstance(x, dict) and x.get(key) == value

    nested_value = "nested_value"
    new_dict_for_update = {
        "name": "updated_value"
    }
    dict_obj = {
        "a": {
            "b": {
                "name": "value",
                "b_nested": {
                    "name": nested_value,
                },
            },
            "c": 1,
            "d": 31,
        }
    }

    dpath.util.set(dict_obj, '/a/*', new_dict_for_update, afilter=partial(afilter, "name", "value"), only_leaves=False,
                   update_dict=True)

    assert dict_obj["a"]["b"]["b_nested"]["name"] == nested_value
    assert dict_obj["a"]["b"]["name"] == new_dict_for_update["name"]

    dict_obj = {
        "a": {
            "b": {
                "name": "value",
                "b_nested": {
                    "name": nested_value,
                },
            },
            "c": 1,
            "d": 31,
        }
    }

    dpath.util.set(dict_obj, ["a", "*"], new_dict_for_update, afilter=partial(afilter, "name", "value"),
                   only_leaves=False, update_dict=True)

    assert dict_obj["a"]["b"]["b_nested"]["name"] == nested_value
    assert dict_obj["a"]["b"]["name"] == new_dict_for_update["name"]


def test_set_existing_path_with_separator():
    dict = {
        "a": {
            'b/c/d': 0,
        },
    }

    dpath.util.set(dict, ['a', 'b/c/d'], 1)
    assert(len(dict['a']) == 1)
    assert(dict['a']['b/c/d'] == 1)
