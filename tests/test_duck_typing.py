#!/usr / bin / env python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
#
# (C) Alain Lichnewsky, 2022
#
#     Test for handling structures that mix dicts and lists (possibly other
#     iterables)
#

import dpath as DP
import unittest
import re
import sys
import rapidfuzz
from dpath.options import isinstance_ext

# check that how the options have been set
print(f"At entry in test_path_ext DPATH_ACCEPT_RE_REGEXP = {DP.options.DPATH_ACCEPT_RE_REGEXP}", file=sys.stderr)

if not DP.options.DPATH_ACCEPT_RE_REGEXP:
    print("This test doesn't make sense with DPATH_ACCEPT_RE_REGEXP = False", file=sys.stderr)
    DP.options.DPATH_ACCEPT_RE_REGEXP = True  # enable re.regexp support in path expr.


print(f"PEP544_PROTOCOL_AVAILABLE={DP.options.PEP544_PROTOCOL_AVAILABLE}", file=sys.stderr)


class TestLangProc(unittest.TestCase):
    """This tests the language processor support of 'typing' module  (Protocol,
    runtime_checkable), and the abilty to test types """

    def test1(self):
        if not DP.options.PEP544_PROTOCOL_AVAILABLE:
            print("Test1 PEPS544 Protocol not available", file=sys.stderr)

        class Anagram():
            def __init__(self, s):
                self.ref = "".join(sorted(s))

            def match(self, st):
                retval = True if "".join(sorted(st)) == self.ref else None
                return retval

        ana = Anagram("sire")
        test_cases = (
            (ana, Anagram, True),
            (ana, DP.types.Duck_StringMatcher, True),
            (ana, DP.types.StringMatcher_aslist, True),
            ("ana", Anagram, False),
            ("ana", DP.types.Duck_StringMatcher, False),
            ("ana", DP.types.StringMatcher_aslist, False),
            (re.compile("ana"), DP.types.Duck_StringMatcher, True),
            (re.compile("ana"), DP.types.StringMatcher_aslist, True),
            (re.compile("ana"), DP.types.Basic_StringMatcher, False),
        )
        success = True
        for (o, c, e) in test_cases:
            r = isinstance_ext(o, c)
            exp = "OK" if (e == r) else "Unexpected"
            print(f"{exp} isinstance({o},{c}) returns {r} expected {e}",
                  file=sys.stderr)
            if (e != r):
                success = False
        assert success
        print("Performed TestLangProc", file=sys.stderr)


class TestBasics(unittest.TestCase):
    """ This tests mixing lists with dicts, inspired by Issue #178
    """

    tble = [{'info': {'label': 'a',
                      'placeholder': 'A',
                      'value': 'some text'}
             },
            {'info': {'label': 'b',
                      'placeholder': 'B',
                      'value': ''}},
            {'info': {'label': 'c',
                      'placeholder': 'C',
                      'value': ''}},
            {2: [{'a': "A", 'b': "B"},
                 {'aa': "AA", 'bb': "BB"}]}
            ]

    mydict = {"first": [{'info': {'label': 'a',
                                  'placeholder': 'A',
                                  'value': 'some text'}
                         },
                        {'info': {'label': 'b',
                                  'placeholder': 'B',
                                  'value': ''}},
                        {'info': {'label': 'c',
                                  'placeholder': 'C',
                                  'value': ''}}],
              2: [{'a': "A", 'b': "B"},
                  {'aa': "AA", 'bb': "BB"}
                  ]
              }

    def testtypes(self):
        """ Test types
        """
        print("Entered TestBasics.testtypes", file=sys.stderr)

        str1 = "a string"
        if isinstance_ext(str1, DP.types.Duck_StringMatcher):
            raise RuntimeError("A string should not be accepted as a StringMatcher")

        rex = re.compile(r"\d+")
        assert isinstance_ext(rex, DP.types.Duck_StringMatcher)

        class Anagram():
            def __init__(self, s):
                self.ref = "".join(sorted(s))

            def match(self, st):
                retval = True if "".join(sorted(st)) == self.ref else None
                return retval

        class Weird():
            def __init__(self, s):
                self.s = s

        class Bad():
            pass

        print(f"PEP544_PROTOCOL_AVAILABLE={DP.options.PEP544_PROTOCOL_AVAILABLE}", file=sys.stderr)
        ana = Anagram("tryit")
        assert isinstance_ext(ana, DP.types.Duck_StringMatcher)
        catAna = isinstance_ext(ana, DP.types.Duck_StringMatcher)
        print(f"Anagram is instance Duck_StringMatcher={catAna}", file=sys.stderr)
        catWeird = isinstance_ext(Weird("oh"), DP.types.Duck_StringMatcher)
        print(f"Weird is instance Duck_StringMatcher={catWeird}", file=sys.stderr)
        catBad = isinstance_ext(Bad(), DP.types.Duck_StringMatcher)
        print(f"Bad is instance Duck_StringMatcher={catBad}", file=sys.stderr)

    def test1(self):
        """ Test1: reference, test extended glob with embedded re.regex
        """
        print("Entered test1", file=sys.stderr)

        mydict = TestBasics.mydict

        r1 = DP.search(mydict, '**/placeholder')
        r2 = DP.search(mydict, '**/{plac\\S+r$}')
        assert r1 == r2

    def test2(self):
        """ Test2: using a StringMatcher duck typed class
        """
        print("Entered test2", file=sys.stderr)

        class MySM():
            def match(self, st):
                return st == "placeholder"

        mydict = TestBasics.mydict

        r1 = DP.search(mydict, '**/placeholder', afilter=lambda x: 'C' == x)
        r2 = DP.search(mydict, ['**', MySM()], afilter=lambda x: 'C' == x)
        r3 = DP.search(mydict, '**/{plac\\S+r$}', afilter=lambda x: 'C' == x)

        assert r1 == r2
        assert r1 == r3

    def test3(self):
        """ Test3: using a StringMatcher (duck typed or derivative) class
        """
        print("Entered test3 (anagram)", file=sys.stderr)
        print(f"PEP544_PROTOCOL_AVAILABLE={DP.options.PEP544_PROTOCOL_AVAILABLE}", file=sys.stderr)

        if DP.options.PEP544_PROTOCOL_AVAILABLE:
            class Anagram():
                def __init__(self, s):
                    self.ref = "".join(sorted(s))

                def match(self, st):
                    retval = True if "".join(sorted(st)) == self.ref else None
                    return retval
        else:
            class Anagram(DP.types.Basic_StringMatcher):
                def __init__(self, s):
                    self.ref = "".join(sorted(s))

                def match(self, st):
                    retval = True if "".join(sorted(st)) == self.ref else None
                    return retval

        mydict = TestBasics.mydict

        r1 = DP.search(mydict, "**/label")
        r2 = DP.search(mydict, ['**', Anagram("bella")])
        print(f"Explicit {r1}", file=sys.stderr)
        print(f"Anagram {r2}", file=sys.stderr)
        expected = {'first': [{'info': {'label': 'a'}},
                              {'info': {'label': 'b'}},
                              {'info': {'label': 'c'}}]}
        assert r1 == r2
        assert r1 == expected

    def test4(self):
        """ Test4: using a StringMatcher (duck typed or derivative) class (with RapidFuzz pkg
            https://github.com/maxbachmann/RapidFuzz)
        """
        print("Entered test4", file=sys.stderr)

        class Approx():
            def __init__(self, s, quality=90):
                self.ref = s
                self.quality = quality

            def match(self, st):
                fratio = rapidfuzz.fuzz.ratio(st, self.ref)
                retval = True if fratio > self.quality else None
                return retval

        mydict = TestBasics.mydict

        r1 = DP.search(mydict, "**/placeholder")
        r2 = DP.search(mydict, ['**', Approx("placecolder")])
        r3 = DP.search(mydict, ['**', Approx("acecolder", 75)])
        print(f"Explicit {r1}", file=sys.stderr)
        print(f"Approx {r2}", file=sys.stderr)
        print(f"Approx {r3}", file=sys.stderr)
        expected = {'first': [{'info': {'placeholder': 'A'}},
                              {'info': {'placeholder': 'B'}},
                              {'info': {'placeholder': 'C'}}]}
        assert r1 == r2
        assert r1 == r3
        assert r1 == expected


if __name__ == "__main__":

    # To debug under the Python debugger:
    # A) Use a command like:
    #    PYTHONPATH="../dpath-source"  python3 -m pdb \
    #             ../dpath-source/tests/test_various_exts.py
    # B) Adapt and uncomment the following
    # ts = TestLangProc()
    # ts.test1()

    # ts = TestBasics()
    # ts.testtypes()
    # ts.test1()
    # ts.test2()
    # ts.test3()
    # ts.test4()

    print("""
    a) This is intended to be run under nose2 and not standalone !
    b) Python script nose_runner (in test-utils) adds to nose2 capability to set dpath.options

    Exiting
    """,
          file=sys.stderr
          )
    sys.exit(2)
