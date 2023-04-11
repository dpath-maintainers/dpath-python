#!/usr / bin / env python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
#
# (C) Alain Lichnewsky, 2022, 2023
#
# Tests of generalized path segment match using ad-hoc matcher objects
#

import dpath as DP
import unittest
import re
import sys
import rapidfuzz


def _sprint(*args, **kwdargs):
    print(*args, **kwdargs, file=sys.stderr)


# check that how the options have been set
_sprint(f"At entry in test_path_ext DPATH_ACCEPT_RE_REGEXP = {DP.options.DPATH_ACCEPT_RE_REGEXP}")

if not DP.options.DPATH_ACCEPT_RE_REGEXP:
    _sprint("This test only works with DPATH_ACCEPT_RE_REGEXP = True")
    DP.options.DPATH_ACCEPT_RE_REGEXP = True  # enable re.regexp support in path expr.

if DP.options.PEP544_PROTOCOL_AVAILABLE:
    _sprint(f"\tPEP544_PROTOCOL_AVAILABLE={DP.options.PEP544_PROTOCOL_AVAILABLE}")
    _sprint("\tWhen True, this permits duck typing, only available since Python3.8")


class TestLangProc(unittest.TestCase):
    """This tests the language processor support of 'typing' module  (Protocol,
    runtime_checkable), and the abilty to test types """

    def test1(self):
        if not DP.options.PEP544_PROTOCOL_AVAILABLE:
            _sprint("Test1 PEPS544 Protocol not available")

        class Anagram():
            def __init__(self, s):
                self.ref = "".join(sorted(s))

            def match(self, st):
                retval = True if "".join(sorted(st)) == self.ref else None
                return retval

        ana = Anagram("sire")
        test_cases = [
            (ana, Anagram, True),
            ("ana", Anagram, False),
            ("ana", DP.types.StringMatcher_astuple, False),
            (re.compile("ana"), DP.types.StringMatcher_astuple, True),
            (re.compile("ana"), DP.types.Basic_StringMatcher, False)]

        if DP.options.PEP544_PROTOCOL_AVAILABLE:
            # these require Python > 3.7
            test_cases.extend([
                (ana, DP.types.Duck_StringMatcher, True),
                (ana, DP.types.StringMatcher_astuple, True),
                ("ana", DP.types.Duck_StringMatcher, False),
                (re.compile("ana"), DP.types.Duck_StringMatcher, True)])
        else:
            # This executes when Python < 3.7, but rejects object ana
            # since it is neither a re.Pattern, nor derived from BasicStringMatcher.
            # Shows that object ana requires non available duck typing!
            test_cases.extend([(ana, DP.types.StringMatcher_astuple, False)])

        success = True
        for (o, c, e) in test_cases:
            r = isinstance(o, c)
            exp = "OK" if (e == r) else "Unexpected"
            _sprint(f"isinstance({o},{c}) returns {r} expected {e}: {exp}")
            if (e != r):
                success = False
        assert success
        _sprint("Performed TestLangProc.test1")


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

    def testDuckStringMatcher(self):
        """ Test types
        """
        _sprint(f"PEP544_PROTOCOL_AVAILABLE={DP.options.PEP544_PROTOCOL_AVAILABLE}")
        if not DP.options.PEP544_PROTOCOL_AVAILABLE:
            _sprint("skipping TestBasics.testDuckStringMatcher, not available for Python <= 3.7")
            return
        _sprint("Entered TestBasics.testDuckStringMatcher")

        str1 = "a string"
        if isinstance(str1, DP.types.Duck_StringMatcher):
            raise RuntimeError("A string should not be accepted as a StringMatcher")

        rex = re.compile(r"\d+")
        assert isinstance(rex, DP.types.Duck_StringMatcher)

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

        ana = Anagram("tryit")
        catAna = isinstance(ana, DP.types.Duck_StringMatcher)
        _sprint(f"Anagram is instance Duck_StringMatcher={catAna}")
        assert catAna

        catWeird = isinstance(Weird("oh"), DP.types.Duck_StringMatcher)
        _sprint(f"Weird is instance Duck_StringMatcher={catWeird}")
        assert not catWeird

        catBad = isinstance(Bad(), DP.types.Duck_StringMatcher)
        _sprint(f"Bad is instance Duck_StringMatcher={catBad}")
        assert not catBad

    def test1(self):
        """ Test1: reference, test extended glob with embedded re.regex
        """
        _sprint("Entered test1")

        mydict = TestBasics.mydict

        r1 = DP.search(mydict, '**/placeholder')
        r2 = DP.search(mydict, '**/{plac\\S+r$}')
        assert r1 == r2
        _sprint("TestBasics.test1 : PASSED")

    def test2(self):
        """ Test2: using a StringMatcher duck typed class
        """
        if not DP.options.PEP544_PROTOCOL_AVAILABLE:
            _sprint("TestBasics.test2 disabled, cannot use PEPS544 Protocol with this Python")
            return

        _sprint("Entered test2")

        class MySM():
            def match(self, st):
                return st == "placeholder"

        mydict = TestBasics.mydict

        r1 = DP.search(mydict, '**/placeholder', afilter=lambda x: 'C' == x)
        r2 = DP.search(mydict, ['**', MySM()], afilter=lambda x: 'C' == x)
        r3 = DP.search(mydict, '**/{plac\\S+r$}', afilter=lambda x: 'C' == x)

        assert r1 == r2
        assert r1 == r3
        _sprint("TestBasics.test2 : PASSED")

    def test3(self):
        """ Test3: using a StringMatcher (duck typed or derivative) class, according to
            Python version's ability.
        """
        # This test corresponds to example in README.rst

        _sprint("Entered test3 (anagram)")
        _sprint(f"PEP544_PROTOCOL_AVAILABLE={DP.options.PEP544_PROTOCOL_AVAILABLE}")

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
        _sprint(f"Explicit {r1}")
        _sprint(f"Anagram {r2}")
        expected = {'first': [{'info': {'label': 'a'}},
                              {'info': {'label': 'b'}},
                              {'info': {'label': 'c'}}]}
        assert r1 == r2
        assert r1 == expected
        _sprint("TestBasics.test3 : PASSED")

    def test4(self):
        """ Test4: using a StringMatcher (duck typed or derivative) class (with RapidFuzz pkg
            https://github.com/maxbachmann/RapidFuzz)
        """
        # This test corresponds to example in README.rst

        _sprint("Entered test4")

        if DP.options.PEP544_PROTOCOL_AVAILABLE:
            class Approx():
                def __init__(self, s, quality=90):
                    self.ref = s
                    self.quality = quality

                def match(self, st):
                    fratio = rapidfuzz.fuzz.ratio(st, self.ref)
                    retval = True if fratio > self.quality else None
                    return retval
        else:
            class Approx(DP.types.Basic_StringMatcher):
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
        _sprint(f"Explicit {r1}")
        _sprint(f"Approx {r2}")
        _sprint(f"Approx {r3}")
        expected = {'first': [{'info': {'placeholder': 'A'}},
                              {'info': {'placeholder': 'B'}},
                              {'info': {'placeholder': 'C'}}]}
        assert r1 == r2
        assert r1 == r3
        assert r1 == expected
        _sprint("TestBasics.test4 : PASSED")
