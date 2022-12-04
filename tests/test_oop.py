from dpath import DDict


def test_getitem():
    d = DDict({
        "a": 1,
        "b": [12, 23, 34],
    })

    assert d["a"] == 1
    assert d["b/0"] == 12
    # assert d["b/-1"] == 34


def test_setitem():
    d = DDict({
        "a": 1,
        "b": [12, 23, 34],
    })

    d["b/5"] = 1
    assert d["b"][5] == 1

    d["c"] = [54, 43, 32, 21]
    assert d["c"] == [54, 43, 32, 21]


def test_setitem_overwrite():
    d = DDict({
        "a": 1,
        "b": [12, 23, 34],
    })

    d["b"] = "abc"
    assert d["b"] == "abc"
