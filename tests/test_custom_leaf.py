import dpath.util
from decimal import Decimal



def test_Decimal():
    testdict = {
        "A" : [
            Decimal(1.5),
            Decimal(2.25)
        ]
    }
    assert dpath.util.get(testdict, "A")[0] == Decimal(1.5)
    assert dpath.util.get(testdict, "A/0") == Decimal(1.5) 
    assert dpath.util.get(testdict, "A/1") == Decimal(2.25)


def test_custom_els():
    func = lambda x: x

    testdict = {
        "A": func,
        "B" : [
            {'a', 'b'}
        ],
    }

    assert dpath.util.get(testdict, "A") == func
    assert dpath.util.get(testdict, "B/0") == {'a', 'b'}


class MappableButNotIterable:
    def __getitem__(self, item):
        if item in (0, 3,  "hi"):
            return 4
        else:
            raise KeyError("item {} not found".format(item))


def test_obtuse_els():
    testdict = {
        "C": {
            "el1" : range(10),
            "el2" : MappableButNotIterable()
        }
    }
    assert list(dpath.util.get(testdict, "C/el1")) == list(range(10))
    assert dpath.util.get(testdict, "C/el2") is not None



def test_odd_mappable():
    testdict = {
        "C": {
            "el2" : MappableButNotIterable()
        }
    }
    try:
        # this should work since this obj is actually mappable
        # it doesn't since we walk across it's keys which causes an error
        assert dpath.util.get(testdict, "C/el2/3") == testdict["C"]["el2"][3]
    except:
        import nose
        raise nose.SkipTest
    else:
        assert False, "Test no longer expected fail, please edit"