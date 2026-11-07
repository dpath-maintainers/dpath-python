import dpath


def test_util_safe_path_list():
    res = dpath._split_path(["Ignore", "the/separator"], None)

    assert len(res) == 2
    assert res[0] == "Ignore"
    assert res[1] == "the/separator"


def test_multichar_separator_keeps_partial_prefix():
    assert dpath._split_path('appleabkey', 'ab') == ['apple', 'key']
    assert dpath._split_path('bakerabkey', 'ab') == ['baker', 'key']
    assert dpath._split_path(':name::key', '::') == [':name', 'key']


def test_multichar_separator_strips_complete_leading_separators():
    assert dpath._split_path('abappleabkey', 'ab') == ['apple', 'key']
    assert dpath._split_path('ababappleabkey', 'ab') == ['apple', 'key']
    assert dpath._split_path(':::name::key', '::') == [':name', 'key']


def test_custom_separator_gets_the_requested_key():
    data = {'apple': {'key': 1}, 'pple': {'key': 2}}
    assert dpath.get(data, 'appleabkey', separator='ab') == 1


def test_custom_separator_new_does_not_create_a_truncated_key():
    data = {}
    dpath.new(data, 'appleabkey', 1, separator='ab')
    assert data == {'apple': {'key': 1}}


def test_custom_separator_set_delete_and_search():
    data = {'apple': {'key': 1}, 'pple': {'key': 2}}
    assert dpath.set(data, 'appleabkey', 3, separator='ab') == 1
    assert data == {'apple': {'key': 3}, 'pple': {'key': 2}}
    assert dpath.search(data, 'appleabkey', separator='ab') == {'apple': {'key': 3}}
    assert dpath.delete(data, 'appleabkey', separator='ab') == 1
    assert data == {'apple': {}, 'pple': {'key': 2}}


def test_separator_prefix_controls():
    assert dpath._split_path('///apple/key', '/') == ['apple', 'key']
    assert dpath._split_path('  apple key', None) == ['apple', 'key']
    path = ['appleabkey']
    assert dpath._split_path(path, 'ab') is path
    try:
        dpath._split_path('apple', '')
    except ValueError:
        pass
    else:
        raise AssertionError('An empty separator must still raise ValueError')
