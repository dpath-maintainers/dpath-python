import nose
from nose.tools import raises
import dpath.path
import dpath.exceptions

@raises(dpath.exceptions.InvalidKeyName)
def test_path_paths_invalid_keyname():
    tdict = {
        "I/contain/the/separator": 0
        }
    for x in dpath.path.paths(tdict):
        pass

def test_path_paths_int_keys():
    dpath.path.validate([
            ['I', dict],
            ['am', dict],
            ['path', dict],
            [0, dict],
            ['of', dict],
            [2, int]
            ])
