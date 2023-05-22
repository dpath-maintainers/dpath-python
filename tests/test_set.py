from functools import partial

import dpath


def test_set_existing_separator():
    dict = {
        "a": {
            "b": 0,
        },
    }

    dpath.set(dict, ';a;b', 1, separator=";")
    assert dict['a']['b'] == 1

    dict['a']['b'] = 0
    dpath.set(dict, ['a', 'b'], 1, separator=";")
    assert dict['a']['b'] == 1


def test_set_existing_dict():
    dict = {
        "a": {
            "b": 0,
        },
    }

    dpath.set(dict, '/a/b', 1)
    assert dict['a']['b'] == 1

    dict['a']['b'] = 0
    dpath.set(dict, ['a', 'b'], 1)
    assert dict['a']['b'] == 1


def test_set_existing_dict_not_affected_by_update_dict_flag():
    dict = {
        "a": {
            "b": 0,
        },
    }

    dpath.set(dict, '/a/b', 1, is_dict_update=True)
    assert (dict['a']['b'] == 1)

    dict['a']['b'] = 0
    dpath.set(dict, ['a', 'b'], 1, is_dict_update=True)
    assert (dict['a']['b'] == 1)


def test_set_existing_list():
    dict = {
        "a": [
            0,
        ],
    }

    dpath.set(dict, '/a/0', 1)
    assert dict['a'][0] == 1

    dict['a'][0] = 0
    dpath.set(dict, ['a', '0'], 1)
    assert dict['a'][0] == 1


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

    dpath.set(dict, '/a/*', 31337, afilter=afilter)
    assert dict['a']['b'] == 0
    assert dict['a']['c'] == 1
    assert dict['a']['d'] == 31337

    dict = {
        "a": {
            "b": 0,
            "c": 1,
            "d": 31,
        }
    }

    dpath.set(dict, ['a', '*'], 31337, afilter=afilter)
    assert dict['a']['b'] == 0
    assert dict['a']['c'] == 1
    assert dict['a']['d'] == 31337


def test_set_filter_not_only_leaves():
    def afilter(key, value, x):
        return isinstance(x, dict) and x.get(key) == value

    dict_obj = {
        "a": {
            "b": {
                "some_known_key": "some_known_key_value",
                "b_nested": {
                    "name": "value",
                },
            },
            "c": 1,
            "d": {
                "some_known_key": "some_other_known_key_value",
                "b_nested": {
                    "name": "value",
                },
            },
            "e": 31,
        }
    }
    new_value = "new_value"

    dpath.set(
        dict_obj,
        '/a/b/*',
        new_value,
        afilter=partial(afilter, "some_known_key", "some_other_known_key_value"),
        is_only_leaves_filter=False
    )
    assert dict_obj["a"]["b"]["b_nested"]["name"] == "value"
    assert dict_obj["a"]["d"] == new_value

    dict_obj = {
        "a": {
            "b": {
                "some_known_key": "some_known_key_value",
                "b_nested": {
                    "name": "value",
                },
            },
            "c": 1,
            "d": {
                "some_known_key": "some_other_known_key_value",
                "b_nested": {
                    "name": "value",
                },
            },
            "e": 31,
        }
    }
    new_value = "new_value"

    dpath.set(
        dict_obj,
        ["a", "b", "*"],
        new_value,
        afilter=partial(afilter, "some_known_key", "some_other_known_key_value"),
        is_only_leaves_filter=False
    )

    assert dict_obj["a"]["b"]["b_nested"]["name"] == "value"
    assert dict_obj["a"]["d"] == new_value


def test_set_filter_not_only_leaves_and_update_dict_flag():
    def afilter(key, value, x):
        return isinstance(x, dict) and x.get(key) == value

    new_dict_for_update = {
        "name": "updated_value",
        "some_other_value": 100
    }
    dict_obj = {
        "a": {
            "b": {
                "some_known_key": "some_known_key_value",
                "name": "some_name",
                "b_nested": {
                    "name": "some_nested_value",
                },
                "some_other_value": 33
            },
            "c": 1,
            "d": 31,
        }
    }

    dpath.set(
        dict_obj,
        '/a/*',
        new_dict_for_update,
        afilter=partial(afilter, "some_known_key", "some_known_key_value"),
        is_only_leaves_filter=False,
        is_dict_update=True
    )

    assert dict_obj["a"]["b"]["name"] == new_dict_for_update["name"]
    assert dict_obj["a"]["b"]["some_other_value"] == \
           new_dict_for_update["some_other_value"]

    dict_obj = {
        "a": {
            "b": {
                "some_known_key": "some_known_key_value",
                "name": "some_name",
                "b_nested": {
                    "name": "some_nested_value",
                },
                "some_other_value": 33
            },
            "c": 1,
            "d": 31,
        }
    }

    dpath.set(
        dict_obj,
        ["a", "*"],
        new_dict_for_update,
        afilter=partial(afilter, "some_known_key", "some_known_key_value"),
        is_only_leaves_filter=False,
        is_dict_update=True
    )

    assert dict_obj["a"]["b"]["name"] == new_dict_for_update["name"]
    assert dict_obj["a"]["b"]["some_other_value"] == \
           new_dict_for_update["some_other_value"]


def test_set_existing_path_with_separator():
    dict = {
        "a": {
            'b/c/d': 0,
        },
    }

    dpath.set(dict, ['a', 'b/c/d'], 1)
    assert len(dict['a']) == 1
    assert dict['a']['b/c/d'] == 1
