import nose
from nose.tools import raises
import dpath.path
import dpath.exceptions
import dpath.options

@raises(dpath.exceptions.InvalidKeyName)
def test_path_paths_empty_key_disallowed():
    tdict = {
        "Empty": {
            "": {
                "Key": ""
            }
        }
    }
    for x in dpath.path.paths(tdict):
        pass

def test_path_paths_empty_key_allowed_skip_false():
    tdict = {
        "Empty": {
            "": {
                "Key": ""
            }
        }
    }
    parts=[]
    dpath.options.ALLOW_EMPTY_STRING_KEYS=True
    for x in dpath.path.paths(tdict, dirs=False, leaves=True, skip=False):
        path = x
    for x in path[:-1]:
        parts.append(x[0])
    dpath.options.ALLOW_EMPTY_STRING_KEYS=False
    assert("/".join(parts) == "Empty//Key")

def test_path_paths_empty_key_allowed_skip_false():
    tdict = {
        "Empty": {
            "": {
                "Key": ""
            }
        }
    }
    # Confirm this works when skip=True (e.g. when coming through dpath.util.get(..)
    parts=[]
    dpath.options.ALLOW_EMPTY_STRING_KEYS=True
    for x in dpath.path.paths(tdict, dirs=False, leaves=True, skip=True):
        path = x
    for x in path[:-1]:
        parts.append(x[0])
    dpath.options.ALLOW_EMPTY_STRING_KEYS=False
    assert("/".join(parts) == "Empty//Key")

def test_path_paths_int_keys():
    dpath.path.validate([
            ['I', dict],
            ['am', dict],
            ['path', dict],
            [0, dict],
            ['of', dict],
            [2, int]
            ])

def test_path_paths_unicode_keys():
    tdict = {
        u"Key Contains Unicode \u00af\u00f5": "value does not",
    }
    paths = list(dpath.path.paths(tdict))
