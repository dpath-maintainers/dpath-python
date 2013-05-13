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
