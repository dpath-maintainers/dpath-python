from copy import deepcopy

from dpath import DDict


def test_oop_getitem():
    d = DDict({
        "a": 1,
        "b": [12, 23, 34],
    })

    assert d["a"] == 1
    assert d["b/0"] == 12
    # assert d["b/-1"] == 34


def test_oop_setitem():
    d = DDict({
        "a": 1,
        "b": [12, 23, 34],
    })

    d["b/5"] = 1
    assert d["b"][5] == 1

    d["c"] = [54, 43, 32, 21]
    assert d["c"] == [54, 43, 32, 21]


def test_oop_delitem():
    d = DDict({
        "a": 1,
        "b": [12, 23, 34],
        "c": {
            "d": {
                "e": [56, 67]
            }
        }
    })

    del d["a"]
    assert "a" not in d

    del d["c/**/1"]
    assert 67 not in d["c/d/e"]


def test_oop_pop():
    d = DDict({
        "a": 1,
        "b": [12, 23, 34],
        "c": {
            "d": {
                "e": [56, 67]
            }
        }
    })
    before = deepcopy(d)

    popped = d.pop("a")
    assert popped == {"a": 1}

    d = deepcopy(before)
    popped = d.pop("b/1")
    assert popped == {"b": [None, 23]}

    d = deepcopy(before)
    popped = d.pop("c/**/1")
    assert popped == {
        "c": {
            "d": {
                "e": [None, 67]
            }
        }
    }


def test_oop_setitem_overwrite():
    d = DDict({
        "a": 1,
        "b": [12, 23, 34],
    })

    d["b"] = "abc"
    assert d["b"] == "abc"


def test_oop_contains():
    d = DDict({
        "a": 1,
        "b": [12, 23, 34],
        "c": {
            "d": {
                "e": [56, 67]
            }
        }
    })

    assert "a" in d
    assert "b" in d
    assert "b/0" in d
    assert "c/d/e/1" in d


def test_oop_merge():
    d = DDict({
        "a": 1,
        "b": [12, 23, 34],
        "c": {
            "d": {
                "e": [56, 67]
            }
        }
    })

    expected_after = {
        "a": 1,
        "b": [12, 23, 34],
        "c": {
            "d": {
                "e": [56, 67]
            }
        },
        "f": [54],
    }

    before = deepcopy(d)

    assert d | {"f": [54]} == expected_after

    assert d == before

    d |= {"f": [54]}

    assert d != before
    assert d == expected_after


def test_oop_len():
    d = DDict({
        "a": 1,
        "b": [12, 23, 34],
        "c": {
            "d": {
                "e": [56, 67]
            }
        }
    })

    assert len(d) == 10, len(d)

    d.recursive_items = False
    assert len(d) == 3, len(d)


def test_oop_keys():
    d = DDict({
        "a": 1,
        "b": [12, 23, 34],
        "c": {
            "d": {
                "e": [56, 67]
            }
        }
    })

    assert not {
        "a",
        "b",
        "c",
        "b/0",
        "b/1",
        "b/2",
        "c/d",
        "c/d/e",
        "c/d/e/0",
        "c/d/e/1",
    }.difference(set(d.keys()))


def test_oop_setdefault():
    d = DDict({
        "a": 1,
        "b": [12, 23, 34],
        "c": {
            "d": {
                "e": [56, 67]
            }
        }
    })

    res = d.setdefault("a", 345)
    assert res == 1

    res = d.setdefault("c/4", 567)
    assert res == 567
    assert d["c"]["4"] == res

    res = d.setdefault("b/6", 89)
    assert res == 89
    assert d["b"] == [12, 23, 34, None, None, None, 89]
