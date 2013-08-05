import nose
import dpath.util

def test_set_existing_separator():
    dict = {
        "a": {
            "b": 0
            }
        }
    dpath.util.set(dict, ';a;b', 1, separator=";")
    assert(dict['a']['b'] == 1)

def test_set_existing_dict():
    dict = {
        "a": {
            "b": 0
            }
        }
    dpath.util.set(dict, '/a/b', 1)
    assert(dict['a']['b'] == 1)

def test_set_existing_list():
    dict = {
        "a": [
            0
            ]
        }
    dpath.util.set(dict, '/a/0', 1)
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
            "d": 31
            }
        }
    dpath.util.set(dict, '/a/*', 31337, afilter=afilter)
    print dict
    assert (dict['a']['b'] == 0)
    assert (dict['a']['c'] == 1)
    assert (dict['a']['d'] == 31337)
