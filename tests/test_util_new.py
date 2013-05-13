import nose
import dpath.util

def test_set_new_dict():
    dict = {
        "a": {
            }
        }
    dpath.util.new(dict, '/a/b', 1)
    assert(dict['a']['b'] == 1)

def test_set_new_list():
    dict = {
        "a": [
            ]
        }
    dpath.util.new(dict, '/a/1', 1)
    assert(dict['a'][1] == 1)
    assert(dict['a'][0] == None)
