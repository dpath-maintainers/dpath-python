# -*- coding: utf-8 -*-
#     making this test autonomous and adding test for other Unicode issues
#     found running under Python2.7
import sys

import unittest

import dpath.util
import dpath.segments as api


class TestEncoding(unittest.TestCase):
    DO_DEBUG_PRINT = False

    def test_unicode_merge(self):
        a = {'中': 'zhong'}
        b = {'文': 'wen'}

        dpath.util.merge(a, b)
        assert(len(a.keys()) == 2)
        assert(a['中'] == 'zhong')
        assert(a['文'] == 'wen')

    def test_unicode_search(self):
        a = {'中': 'zhong'}

        results = [[x[0], x[1]] for x in dpath.util.search(a, '*', yielded=True)]
        assert(len(results) == 1)
        assert(results[0][0] == '中')
        assert(results[0][1] == 'zhong')


    def test_unicode_str_hybrid(self):
        a = {'first': u'1'}
        b = {u'second': '2'}

        dpath.util.merge(a, b)
        assert(len(a.keys()) == 2)
        assert(a[u'second'] == '2')
        assert(a['second'] == u'2')
        assert(a[u'first'] == '1')
        assert(a['first'] == u'1')


# ......................................................................
#  Reproducing an issue in Python2.7, not in Python3, that boiled down to
#  unicode support in api.leaf. This resulted in infinite loop in api.walk
#  In following code: AA will be OK, before correction UU failed as shown below:
#
# Test of api.fold OK
# About to call api.fold with thing=(<type 'unicode'>)UU f=adder
# walk entered with obj=(<type 'unicode'>)UU, location=(<type 'tuple'>)()
# walk entered with obj=(<type 'unicode'>)U, location=(<type 'tuple'>)(0,)
# walk entered with obj=(<type 'unicode'>)U, location=(<type 'tuple'>)(0, 0)
# .... more deleted ...
# RuntimeError: maximum recursion depth exceeded while calling a Python object
# ......................................................................


    def test_reproduce_issue(self):

        def f(o, p, a):
            a[0] += 1

        for thing in ("AA", u"UU"):
            if TestEncoding.DO_DEBUG_PRINT:
                sys.stderr.write("About to call api.fold with thing=(%s)%s f=adder\n"
                                 % (type(thing), thing))
            [count] = api.fold(thing, f, [0])
            assert count == len(tuple(api.walk(thing)))


    def test_reproduce_issue2(self):
        for thing in ("AA", u"UU"):
            if TestEncoding.DO_DEBUG_PRINT:
                sys.stderr.write("About to call walk with arg=(%s)%s\n"
                                 % (type(thing), thing))
            for pair in api.walk(thing):
                sys.stderr.write("pair=%s\n" % repr(pair))

    def test_reproduce_issue3(self):
        for thing in ("AA", u"UU"):
            if TestEncoding.DO_DEBUG_PRINT:
                sys.stderr.write("About to call leaf and kvs with arg=(%s)%s\n"
                                 % (type(thing), thing))
                sys.stderr.write("leaf(%s) => %s \n" % (thing, api.leaf(thing)))
                sys.stderr.write("kvs(%s) => %s \n" % (thing, api.kvs(thing)))
            assert api.leaf(thing)


if __name__ == "__main__":
    if "-h" in sys.argv:
        description = """\
This may run either under tox or standalone. When standalone
flags -h and -v are recognized, other flags are dealt with by unittest.main
and may select test cases.

Flags:
    -h print this help and quit
    -v print information messages on stderr
"""
        print(description)
        sys.exit(0)

    if "-v" in sys.argv:
        sys.argv = [x for x in sys.argv if x != "-v"]
        TestEncoding.DO_DEBUG_PRINT = True
        sys.stderr.write("Set verbose mode\n")

    unittest.main()
