import dpath


def test_util_safe_path_list():
    res = dpath._split_path(["Ignore", "the/separator"], None)

    assert len(res) == 2
    assert res[0] == "Ignore"
    assert res[1] == "the/separator"


def test_split_path_multichar_separator_does_not_strip_characters():
    # A multi-character separator must be treated as a string, not a set of
    # characters. lstrip("ab") would strip any leading 'a'/'b' from the first
    # key, mangling it.
    res = dpath._split_path("appleabkey", "ab")
    assert res == ["apple", "key"], "%r != ['apple', 'key']" % (res,)

    # A genuine leading separator is still stripped (one occurrence).
    res = dpath._split_path("abappleabkey", "ab")
    assert res == ["apple", "key"], "%r != ['apple', 'key']" % (res,)


def test_multichar_separator_get_and_new():
    data = {'apple': {'key': 1}, 'pple': {'key': 2}}
    assert dpath.get(data, 'appleabkey', separator='ab') == 1

    created = {}
    dpath.new(created, 'appleabkey', 1, separator='ab')
    assert created == {'apple': {'key': 1}}, "%r" % (created,)


def test_split_path_single_char_separator_unchanged():
    # Single-character separators keep their existing behavior, including
    # stripping repeated leading separators.
    assert dpath._split_path("/a/b", "/") == ["a", "b"]
    assert dpath._split_path("//a/b", "/") == ["a", "b"]
    assert dpath._split_path("a/b", "/") == ["a", "b"]
