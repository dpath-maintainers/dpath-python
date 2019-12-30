import dpath.segments
import dpath.exceptions


def test_path_get_list_of_dicts():
    tdict = {
        "a": {
            "b": [
                {0: 0},
                {0: 1},
                {0: 2},
            ],
        },
    }
    segments = ['a', 'b', 0, 0]

    res = dpath.segments.view(tdict, segments)
    assert(isinstance(res['a']['b'], list))
    assert(len(res['a']['b']) == 1)
    assert(res['a']['b'][0][0] == 0)
