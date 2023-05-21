# -*- coding: utf-8 -*-
# -*- mode: Python -*-
#
# (C) Alain Lichnewsky, 2022, 2023
#
#     Test support of extended specs with re.regex  in many dpath functions
#
import sys
from os import environ
import re

from copy import copy

import unittest
import dpath as DP
from dpath.exceptions import InvalidRegex

# reusable classes to perform tests on lists of (case, expected result)
import tests.regexpTestLib as T

# Allow for command line/environment setup of verbose output
# The default is not set.
_verbosity = "VERBOSE_TEST" in environ and environ["VERBOSE_TEST"] == "TRUE"


class SampleDicts:

    d1 = {
        "a001": {
            "b2": {
                "c1.2": {
                    "d.dd": 0,
                    "e.ee": 1,
                    "f.f0": 2,
                },
            },
        },
    }

    d2 = {
        "Name": "bridge",
        "Id": "333d22b3724",
        "Created": "2022-12-08T09:02:33.360812052+01:00",
        "Driver": "bridge",
        "EnableIPv6": False,
        "IPAM": {
                "Driver": "default",
                "Options": None,
                "Config":
                {
                    "Subnet": "172.17.0.0/16",
                    "Gateway": "172.17.0.1"
                }},
        "ConfigFrom": {
            "Network": "172.O.0.0/32"},
        "Containers": {
            "199c590e8f13477": {
                "Name": "al_dpath",
                "MacAddress": "02:34:0a:11:10:22",
                "IPv4Address": "172.17.0.2/16",
                "IPv6Address": ""}},
        "Labels": {}}


specs1_A = (([re.compile(".*")], "a001"),
            ([re.compile("[a-z]+$")], None),
            (["*", re.compile(".*")], "a001/b2"),
            (["*", "*", re.compile(".*")], "a001/b2/c1.2"),
            (["*", re.compile("[a-z]+\\d+$")], "a001/b2"),
            (["*", re.compile("[a-z]+[.][a-z]+$")], None),
            (["**", re.compile(".*")], ("a001", "a001/b2", "a001/b2/c1.2", "a001/b2/c1.2/d.dd",
                                        "a001/b2/c1.2/e.ee", "a001/b2/c1.2/f.f0")),
            (["**", re.compile("[a-z]+\\d+$")], ("a001", "a001/b2")),
            (["**", re.compile("[a-z]+[.][a-z]+$")], ('a001/b2/c1.2/d.dd', 'a001/b2/c1.2/e.ee')))

specs1_B = (([re.compile(".*")], True),
            ([re.compile("[a-z]+$")], False),
            (["*", re.compile(".*")], False),
            (["*", "*", re.compile(".*")], False),
            (["*", re.compile("[a-z]+\\d+$")], False),
            (["*", re.compile("[a-z]+[.][a-z]+$")], False),
            (["**", re.compile(".*")], True),
            (["**", re.compile("[a-z]+\\d+$")], True),
            (["**", re.compile("[a-z]+[.][a-z]+$")], False))

specs1_C = (([re.compile(".*")], set()),
            ([re.compile("[a-z]+$")], set()),
            (["*", re.compile(".*")], set()),
            (["*", "*", re.compile(".*")], set()),
            (["*", re.compile("[a-z]+\\d+$")], set()),
            (["*", re.compile("[a-z]+[.][a-z]+$")], set()),
            (["**", re.compile(".*")], set((0, 1, 2))),
            (["**", re.compile("[a-z]+\\d+$")], set()),
            (["**", re.compile("[a-z]+[.][a-z]+$")], set((0, 1))))

specs1_D = (([re.compile(".*")], None),
            ([re.compile("[a-z]+$")], None),
            (["*", re.compile(".*")], None),
            (["*", "*", re.compile(".*")], None),
            (["*", re.compile("[a-z]+\\d+$")], None),
            (["*", re.compile("[a-z]+[.][a-z]+$")], None),
            (["**", re.compile(".*")], ("a001/b2/c1.2/d.dd",
                                        "a001/b2/c1.2/e.ee", "a001/b2/c1.2/f.f0")),
            (["**", re.compile("[a-z]+\\d+$")], None),
            (["**", re.compile("[a-z]+[.][a-z]+$")], ('a001/b2/c1.2/d.dd', 'a001/b2/c1.2/e.ee')))

specs1_View = (([re.compile(".*")], ({'a001': {'b2': {'c1.2': {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}}}},)),
               ([re.compile("[a-z]+$")], ({},)),
               (["*", re.compile(".*")], ({'a001': {'b2': {'c1.2': {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}}}},)),
               (["*", "*", re.compile(".*")], ({'a001': {'b2': {'c1.2': {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}}}},)),
               (["*", re.compile("[a-z]+\\d+$")], ({'a001': {'b2': {'c1.2': {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}}}},)),
               (["*", re.compile("[a-z]+[.][a-z]+$")], ({},)),
               (["**", re.compile(".*")], ({'a001': {'b2': {'c1.2': {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}}}},)), )

specs1_Get = (([re.compile(".*")], {'b2': {'c1.2': {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}}}),
              ([re.compile("[a-z]+$")], (('*NONE*',),)),
              (["*", re.compile(".*")], {'c1.2': {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}}),
              (["*", "*", re.compile(".*")], {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}),
              (["*", re.compile("[a-z]+\\d+$")], {'c1.2': {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}}),
              (["*", re.compile("[a-z]+[.][a-z]+$")], (('*NONE*',),)),
              (["**", re.compile(".*")], ("Exception",)),
              (["**", re.compile("[a-z]+\\d+$")], ("Exception",)),
              (["**", re.compile("[a-z]+[.][a-z]+$")], ("Exception",)),)

specs2_Search = ((["*", re.compile("[A-Z][a-z\\d]*$")],
                  ("IPAM/Driver", "IPAM/Options", "IPAM/Config", "ConfigFrom/Network")),
                 (["**", re.compile("[A-Z][a-z\\d]*$")],
                  ("Name", "Id", "Created", "Driver",
                   "Containers", "Labels", "IPAM/Driver", "IPAM/Options",
                   "IPAM/Config", "IPAM/Config/Subnet", "IPAM/Config/Gateway",
                   "ConfigFrom/Network", "Containers/199c590e8f13477/Name")),
                 (["**", re.compile("[A-Z][A-Za-z\\d]*Address$")],
                  ("Containers/199c590e8f13477/MacAddress", "Containers/199c590e8f13477/IPv4Address",
                   "Containers/199c590e8f13477/IPv6Address")),
                 (["**", re.compile("[A-Za-z]+\\d+$")], ("EnableIPv6",)),
                 (["**", re.compile("\\d+[.]\\d+")], None),

                 # repeated intentionally using raw strings rather than '\\' escapes

                 (["*", re.compile(r"[A-Z][a-z\d]*$")],
                  ("IPAM/Driver", "IPAM/Options", "IPAM/Config", "ConfigFrom/Network")),
                 (["**", re.compile(r"[A-Za-z]+\d+$")], ("EnableIPv6",)),
                 (["**", re.compile(r"\d+[.]\d+")], None))

specs2_SearchPar = (("**/{^[A-Za-z]{2}$}", ("Id",)),
                    ("{^[A-Za-z]{2}$}", ("Id",)),
                    (re.compile("^[A-Za-z]{2}$"), ("Id",)),
                    ("*/{[A-Z][A-Za-z\\d]*$}", ("IPAM/Driver", "IPAM/Options", "IPAM/Config", "ConfigFrom/Network")),
                    ("{.*}/{[A-Z][A-Za-z\\d]*$}", ("IPAM/Driver", "IPAM/Options", "IPAM/Config", "ConfigFrom/Network")),
                    ("**/{[A-Z][A-Za-z\\d]*\\d$}", ("EnableIPv6",)),
                    ("**/{[A-Z][A-Za-z\\d]*Address$}", ("Containers/199c590e8f13477/MacAddress",
                                                        "Containers/199c590e8f13477/IPv4Address",
                                                        "Containers/199c590e8f13477/IPv6Address")),

                    # repeated intentionally using raw strings rather than '\\' escapes

                    (r"**/{[A-Z][A-Za-z\d]*\d$}", ("EnableIPv6",)),)


# one class per function to be tested, postpone tests that need
# DP.options.ALLOW_REGEX == True

class TestSearchAlways():
    def setUp(self):
        if "DPATH_ALLOW_REGEX" in environ:
            DP.options.ALLOW_REGEX = True

    def test1(self):
        T.show(f"In {self.test1}")
        tests = T.Loop(SampleDicts.d1, specs1_A)

        def fn(_data, _spec):
            return DP.search(_data, _spec, yielded=True)

        tests.setVerbose(_verbosity).run(fn)

    def test2(self):
        T.show(f"In {self.test2}")
        tests = T.Loop(SampleDicts.d1, specs1_D)

        def afilter(x):
            if isinstance(x, int):
                return True
            return False

        def fn(_data, _spec):
            return DP.search(_data, _spec, yielded=True, afilter=afilter)

        tests.setVerbose(_verbosity).run(fn)

    def test3(self):
        T.show(f"In {self.test3}")
        tests = T.Loop(SampleDicts.d2, specs2_Search)

        def fn(_data, _spec):
            return DP.search(_data, _spec, yielded=True)

        tests.setVerbose(_verbosity).setPrettyPrint().run(fn)


class TestGet():
    def setUp(self):
        if "DPATH_ALLOW_REGEX" in environ:
            DP.options.ALLOW_REGEX = True

    def test1(self):
        T.show(f"In {self.test1}")
        tests = T.Loop(SampleDicts.d1, specs1_Get)

        def fn(_data, _spec):
            try:
                return ((DP.get(_data, _spec, default=("*NONE*",)), None),)
            except InvalidRegex as err:
                T.show(f"Exception: {err}")
                return (("InvalidRegex", None), )
            except Exception as err:
                T.show(f"Exception: {err}")
                return (("Exception", None), )

        tests.setVerbose(_verbosity).run(fn)


class TestView():
    def setUp(self):
        if "DPATH_ALLOW_REGEX" in environ:
            DP.options.ALLOW_REGEX = True

    def test1(self):
        T.show(f"In {self.test1}")
        tests = T.Loop(SampleDicts.d1, specs1_View)

        def fn(_data, _spec):
            r = DP.segments.view(_data, _spec)
            return ((r, None), )

        tests.setVerbose(_verbosity).run(fn)


class TestMatch():
    def setUp(self):
        if "DPATH_ALLOW_REGEX" in environ:
            DP.options.ALLOW_REGEX = True

    def test1(self):
        T.show(f"In {self.test1}")
        tests = T.Loop(SampleDicts.d1, specs1_B)

        def fn(_data, _spec):
            r = DP.segments.match(_data, _spec)
            return ((r, None), )

        tests.setVerbose(_verbosity).run(fn)


class TestSearch():
    def setUp(self):
        # these tests involve regex in parenthesized strings
        if "DPATH_ALLOW_REGEX" in environ:
            DP.options.ALLOW_REGEX = True

        if DP.options.ALLOW_REGEX is not True:
            DP.options.ALLOW_REGEX = True
            T.show("ALLOW_REGEX == True required for this test: forced")

    def test1(self):
        T.show(f"In {self.test1}")
        tests = T.Loop(SampleDicts.d2, specs2_SearchPar)

        def fn(_data, _spec):
            return DP.search(_data, _spec, yielded=True)

        tests.setVerbose(_verbosity).setPrettyPrint().run(fn)

    def test2(self):
        T.show(f"In {self.test1}")
        specs = (("/**/{zz)bad}", ("InvalidRegex",)),
                 ("{zz)bad}/yyy", ("InvalidRegex",)),
                 ("**/{zz)bad}/yyy", ("InvalidRegex",)),
                 ("**/{zz)bad}/yyy/.*", ("InvalidRegex",)),
                 (123, ("Exception",)))

        tests = T.Loop(SampleDicts.d2, specs)

        def fn(_data, _spec):
            try:
                return DP.search(_data, _spec, yielded=True)
            except InvalidRegex as err:
                if tests.verbose:
                    T.show(f"\tErrMsg: {err}")
                return (("InvalidRegex", None),)
            except Exception as err:
                if tests.verbose:
                    T.show(f"\tErrMsg: {err}")
                return (("Exception", None),)

        tests.setVerbose(_verbosity).setPrettyPrint().run(fn)


class TestDelete(unittest.TestCase):
    def setUp(self):
        # these tests involve regex in parenthesized strings
        if "DPATH_ALLOW_REGEX" in environ:
            DP.options.ALLOW_REGEX = True

        if DP.options.ALLOW_REGEX is not True:
            DP.options.ALLOW_REGEX = True
            T.show("ALLOW_REGEX == True required for this test: forced")

    def test1(self):
        T.show(f"In {self.test1}")
        dict1 = {
            "a": {
                "b": 0,
                "12": 0,
            },
            "a0": {
                "b": 0,
            },
        }

        specs = (re.compile("[a-z]+$"), re.compile("[a-z]+\\d+$"),
                 "{[a-z]+\\d+$}")
        i = 0
        for spec in specs:
            dict = copy(dict1)
            print(f"spec={spec}")
            print(f"Before deletion dict={dict}", file=sys.stderr)
            DP.delete(dict, [spec])
            print(f"After deletion dict={dict}", file=sys.stderr)
            if i == 0:
                assert (dict == {"a0": {"b": 0, }, })
            else:
                assert (dict == {"a": {"b": 0, "12": 0, }})
            i += 1
