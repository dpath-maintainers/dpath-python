from nose2.tools.such import helper

import dpath.segments
import dpath.exceptions
import dpath.options


def test_path_paths_empty_key_disallowed():
    tdict = {
        "Empty": {
            "": {
                "Key": ""
            }
        }
    }

    with helper.assertRaises(dpath.exceptions.InvalidKeyName):
        for x in dpath.segments.walk(tdict):
            pass


def test_path_paths_empty_key_allowed():
    tdict = {
        "Empty": {
            "": {
                "Key": ""
            }
        }
    }

    segments = []
    dpath.options.ALLOW_EMPTY_STRING_KEYS = True

    for segments, value in dpath.segments.leaves(tdict):
        pass

    dpath.options.ALLOW_EMPTY_STRING_KEYS = False
    assert "/".join(segments) == "Empty//Key"
