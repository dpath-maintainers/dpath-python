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


def test_set_existing_path_with_separator():
    dict = {
        "a": {
            'b/c/d': 0,
        },
    }

    dpath.util.set(dict, ['a', 'b/c/d'], 1)
    assert(len(dict['a']) == 1)
    assert(dict['a']['b/c/d'] == 1)
