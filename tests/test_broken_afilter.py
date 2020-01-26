import dpath.util
import sys


def test_broken_afilter():
    def afilter(x):
        if x in [1, 2]:
            return True
        return False

    dict = {
        "a": {
            "view_failure": "a",
            "b": {
                "c": {
                    "d": 0,
                    "e": 1,
                    "f": 2,
                },
            },
        },
    }
    paths = [
        'a/b/c/e',
        'a/b/c/f',
    ]

    for (path, value) in dpath.util.search(dict, '/**', yielded=True, afilter=afilter):
        assert(path in paths)
    assert("view_failure" not in dpath.util.search(dict, '/**', afilter=afilter)['a'])
    assert("d" not in dpath.util.search(dict, '/**', afilter=afilter)['a']['b']['c'])

    for (path, value) in dpath.util.search(dict, ['**'], yielded=True, afilter=afilter):
        assert(path in paths)
    assert("view_failure" not in dpath.util.search(dict, ['**'], afilter=afilter)['a'])
    assert("d" not in dpath.util.search(dict, ['**'], afilter=afilter)['a']['b']['c'])

    def filter(x):
        sys.stderr.write(str(x))
        if hasattr(x, 'get'):
            return x.get('type', None) == 'correct'
        return False

    a = {
        'actions': [
            {
                'type': 'correct'
            },
            {
                'type': 'incorrect'
            },
        ],
    }

    results = [[x[0], x[1]] for x in dpath.util.search(a, 'actions/*', yielded=True)]
    results = [[x[0], x[1]] for x in dpath.util.search(a, 'actions/*', afilter=filter, yielded=True)]
    assert(len(results) == 1)
    assert(results[0][1]['type'] == 'correct')
