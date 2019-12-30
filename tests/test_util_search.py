import dpath.util


def test_search_paths_with_separator():
    dict = {
        "a": {
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
        'a',
        'a;b',
        'a;b;c',
        'a;b;c;d',
        'a;b;c;e',
        'a;b;c;f',
    ]

    for (path, value) in dpath.util.search(dict, '/**', yielded=True, separator=";"):
        assert(path in paths)

    for (path, value) in dpath.util.search(dict, ['**'], yielded=True, separator=";"):
        assert(path in paths)


def test_search_paths():
    dict = {
        "a": {
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
        'a',
        'a/b',
        'a/b/c',
        'a/b/c/d',
        'a/b/c/e',
        'a/b/c/f',
    ]

    for (path, value) in dpath.util.search(dict, '/**', yielded=True):
        assert(path in paths)

    for (path, value) in dpath.util.search(dict, ['**'], yielded=True):
        assert(path in paths)


def test_search_afilter():
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


def test_search_globbing():
    dict = {
        "a": {
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
        'a/b/c/d',
        'a/b/c/f',
    ]

    for (path, value) in dpath.util.search(dict, '/a/**/[df]', yielded=True):
        assert(path in paths)

    for (path, value) in dpath.util.search(dict, ['a', '**', '[df]'], yielded=True):
        assert(path in paths)


def test_search_return_dict_head():
    tdict = {
        "a": {
            "b": {
                0: 0,
                1: 1,
                2: 2,
            },
        },
    }
    res = dpath.util.search(tdict, '/a/b')
    assert(isinstance(res['a']['b'], dict))
    assert(len(res['a']['b']) == 3)
    assert(res['a']['b'] == {0: 0, 1: 1, 2: 2})

    res = dpath.util.search(tdict, ['a', 'b'])
    assert(isinstance(res['a']['b'], dict))
    assert(len(res['a']['b']) == 3)
    assert(res['a']['b'] == {0: 0, 1: 1, 2: 2})


def test_search_return_dict_globbed():
    tdict = {
        "a": {
            "b": {
                0: 0,
                1: 1,
                2: 2,
            },
        },
    }

    res = dpath.util.search(tdict, '/a/b/[02]')
    assert(isinstance(res['a']['b'], dict))
    assert(len(res['a']['b']) == 2)
    assert(res['a']['b'] == {0: 0, 2: 2})

    res = dpath.util.search(tdict, ['a', 'b', '[02]'])
    assert(isinstance(res['a']['b'], dict))
    assert(len(res['a']['b']) == 2)
    assert(res['a']['b'] == {0: 0, 2: 2})


def test_search_return_list_head():
    tdict = {
        "a": {
            "b": [
                0,
                1,
                2,
            ],
        },
    }

    res = dpath.util.search(tdict, '/a/b')
    assert(isinstance(res['a']['b'], list))
    assert(len(res['a']['b']) == 3)
    assert(res['a']['b'] == [0, 1, 2])

    res = dpath.util.search(tdict, ['a', 'b'])
    assert(isinstance(res['a']['b'], list))
    assert(len(res['a']['b']) == 3)
    assert(res['a']['b'] == [0, 1, 2])


def test_search_return_list_globbed():
    tdict = {
        "a": {
            "b": [
                0,
                1,
                2,
            ]
        }
    }

    res = dpath.util.search(tdict, '/a/b/[02]')
    assert(isinstance(res['a']['b'], list))
    assert(len(res['a']['b']) == 3)
    assert(res['a']['b'] == [0, None, 2])

    res = dpath.util.search(tdict, ['a', 'b', '[02]'])
    assert(isinstance(res['a']['b'], list))
    assert(len(res['a']['b']) == 3)
    assert(res['a']['b'] == [0, None, 2])


def test_search_list_key_with_separator():
    tdict = {
        "a": {
            "b": {
                "d": 'failure',
            },
            "/b/d": 'success',
        },
    }

    res = dpath.util.search(tdict, ['a', '/b/d'])
    assert('b' not in res['a'])
    assert(res['a']['/b/d'] == 'success')


def test_search_multiple_stars():
    testdata = {
        'a': [
            {
                'b': [
                    {'c': 1},
                    {'c': 2},
                    {'c': 3},
                ],
            },
        ],
    }
    testpath = 'a/*/b/*/c'

    res = dpath.util.search(testdata, testpath)
    assert(len(res['a'][0]['b']) == 3)
    assert(res['a'][0]['b'][0]['c'] == 1)
    assert(res['a'][0]['b'][1]['c'] == 2)
    assert(res['a'][0]['b'][2]['c'] == 3)
