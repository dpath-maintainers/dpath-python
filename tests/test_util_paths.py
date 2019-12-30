import dpath.util


def test_util_safe_path_list():
    res = dpath.util.__safe_path__(["Ignore", "the/separator"], None)

    assert(len(res) == 2)
    assert(res[0] == "Ignore")
    assert(res[1] == "the/separator")
