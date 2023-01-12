import dpath


def test_set_new_separator():
    dict = {
        "a": {
        },
    }

    dpath.new(dict, ';a;b', 1, separator=";")
    assert dict['a']['b'] == 1

    dpath.new(dict, ['a', 'b'], 1, separator=";")
    assert dict['a']['b'] == 1


def test_set_new_dict():
    dict = {
        "a": {
        },
    }

    dpath.new(dict, '/a/b', 1)
    assert dict['a']['b'] == 1

    dpath.new(dict, ['a', 'b'], 1)
    assert dict['a']['b'] == 1


def test_set_new_list():
    dict = {
        "a": [
        ],
    }

    dpath.new(dict, '/a/1', 1)
    assert dict['a'][1] == 1
    assert dict['a'][0] is None

    dpath.new(dict, ['a', 1], 1)
    assert dict['a'][1] == 1
    assert dict['a'][0] is None


def test_set_list_with_dict_int_ambiguity():
    d = {"list": [{"root": {"1": {"k": None}}}]}

    dpath.new(d, "list/0/root/1/k", "new")

    expected = {"list": [{"root": {"1": {"k": "new"}}}]}

    assert d == expected


def test_int_segment_list_type_check():
    d = {}
    dpath.new(d, "a/b/0/c/0", "hello")
    assert 'b' in d.get("a", {})
    assert isinstance(d["a"]["b"], list)
    assert len(d["a"]["b"]) == 1
    assert 'c' in d["a"]["b"][0]
    assert isinstance(d["a"]["b"][0]["c"], list)
    assert len(d["a"]["b"][0]["c"]) == 1


def test_int_segment_dict_type_check():
    d = {"a": {"b": {"0": {}}}}
    dpath.new(d, "a/b/0/c/0", "hello")
    assert "b" in d.get("a", {})
    assert isinstance(d["a"]["b"], dict)
    assert '0' in d["a"]["b"]
    assert 'c' in d["a"]["b"]["0"]
    assert isinstance(d["a"]["b"]["0"]["c"], list)


def test_set_new_list_path_with_separator():
    # This test kills many birds with one stone, forgive me
    dict = {
        "a": {
        },
    }

    dpath.new(dict, ['a', 'b/c/d', 0], 1)
    assert len(dict['a']) == 1
    assert len(dict['a']['b/c/d']) == 1
    assert dict['a']['b/c/d'][0] == 1


def test_set_new_list_integer_path_with_creator():
    d = {}

    def mycreator(obj, pathcomp, nextpathcomp, hints):
        print(hints)
        print(pathcomp)
        print(nextpathcomp)
        print("...")

        target = pathcomp[0]
        if isinstance(obj, list) and (target.isdigit()):
            target = int(target)

        if ((nextpathcomp is not None) and (isinstance(nextpathcomp, int) or str(nextpathcomp).isdigit())):
            obj[target] = [None] * (int(nextpathcomp) + 1)
            print("Created new list in target")
        else:
            print("Created new dict in target")
            obj[target] = {}
        print(obj)

    dpath.new(d, '/a/2', 3, creator=mycreator)
    print(d)
    assert isinstance(d['a'], list)
    assert len(d['a']) == 3
    assert d['a'][2] == 3
