import dpath.util


def test_unicode_merge():
    a = {'中': 'zhong'}
    b = {'文': 'wen'}

    dpath.util.merge(a, b)
    assert(len(a.keys()) == 2)
    assert(a['中'] == 'zhong')
    assert(a['文'] == 'wen')


def test_unicode_search():
    a = {'中': 'zhong'}

    results = [[x[0], x[1]] for x in dpath.util.search(a, '*', yielded=True)]
    assert(len(results) == 1)
    assert(results[0][0] == '中')
    assert(results[0][1] == 'zhong')


def test_unicode_str_hybrid():
    a = {'first': u'1'}
    b = {u'second': '2'}

    dpath.util.merge(a, b)
    assert(len(a.keys()) == 2)
    assert(a[u'second'] == '2')
    assert(a['second'] == u'2')
    assert(a[u'first'] == '1')
    assert(a['first'] == u'1')
