import nose
from nose.tools import raises
import dpath.path
import dpath.exceptions

def test_path_get_list_of_dicts():
    tdict = {
        "a": {
            "b": [
                {0: 0},
                {0: 1},
                {0: 2}]
            }
        }
    res = dpath.path.get(tdict, dpath.path.path_types(tdict, ['a', 'b', 0, 0]), view=True)
    assert(isinstance(res['a']['b'], list))
    assert(len(res['a']['b']) == 1)
    assert(res['a']['b'][0][0] == 0)
