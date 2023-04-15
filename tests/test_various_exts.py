#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
#
# (C) Alain Lichnewsky, 2022
#
#     Test support of extended specs with re.regex  in many functionalities that use path
#     specifications.
#
import sys
import re

from copy import copy

import unittest
import dpath as DP
from dpath.exceptions import InvalidRegex

# check that how the options have been set
print(f"At entry in test_path_ext DPATH_ACCEPT_RE_REGEXP_IN_STRING = {DP.options.DPATH_ACCEPT_RE_REGEXP_IN_STRING}", file=sys.stderr)

if not DP.options.DPATH_ACCEPT_RE_REGEXP_IN_STRING:
    print("switching to DPATH_ACCEPT_RE_REGEXP_IN_STRING = True", file=sys.stderr)
    DP.options.DPATH_ACCEPT_RE_REGEXP_IN_STRING = True  # enable re.regexp support in path expr.


# one class per function to be tested
class SampleDicts():

    def build(self):
        self.d1 = {
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

        self.specs1 = (([re.compile(".*")], "a001", True, set()),
                       ([re.compile("[a-z]+$")], "a001", False, set()),
                       (["*", re.compile(".*")], "a001", False, set()),
                       (["*", "*", re.compile(".*")], "a001", False, set()),
                       (["*", re.compile("[a-z]+\\d+$")], "a001", False, set()),
                       (["*", re.compile("[a-z]+[.][a-z]+$")], "a001", False, set()),
                       (["**", re.compile(".*")], "a001", True, set((0,1,2))),
                       (["**", re.compile("[a-z]+\\d+$")], "a001", True, set()),
                       (["**", re.compile("[a-z]+[.][a-z]+$")], "a001", False, set((0,1)))
                       )

        self.specs1Pairs = (([re.compile(".*")], ("a001",)),
                            ([re.compile("[a-z]+$")], None),
                            (["*", re.compile(".*")], ("a001/b2",)),
                            (["*", "*", re.compile(".*")], ("a001/b2/c1.2",)),
                            (["*", re.compile("[a-z]+\\d+$")], ("a001/b2",)),
                            (["*", re.compile("[a-z]+[.][a-z]+$")], None),
                            (["**", re.compile(".*")],
                            ("a001", "a001/b2", "a001/b2/c1.2", "a001/b2/c1.2/d.dd",
                             "a001/b2/c1.2/e.ee", "a001/b2/c1.2/f.f0")),
                            (["**", re.compile("[a-z]+\\d+$")], ("a001", "a001/b2")),
                            (["**", re.compile("[a-z]+[.][a-z]+$")],
                            ("a001/b2/c1.2/d.dd", "a001/b2/c1.2/e.ee"))
                            )

        self.specs1GetPairs = (([re.compile(".*")], {'b2': {'c1.2': {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}}}),
                               ([re.compile("[a-z]+$")], ('*NONE*',)),
                               (["*", re.compile(".*")], {'c1.2': {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}}),
                               (["*", "*", re.compile(".*")], {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}),
                               (["*", re.compile("[a-z]+\\d+$")], {'c1.2': {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}}),
                               (["*", re.compile("[a-z]+[.][a-z]+$")], ('*NONE*',)),
                               (["**", re.compile(".*")], "*FAIL*"),
                               (["**", re.compile("[a-z]+\\d+$")], "*FAIL*"),
                               (["**", re.compile("[a-z]+[.][a-z]+$")], "*FAIL*"),
                               )

        self.d2 = {"Name": "bridge",
                   "Id": "333d22b3724",
                   "Created": "2022-12-08T09:02:33.360812052+01:00",
                   "Scope": "local",
                   "Driver": "bridge",
                   "EnableIPv6": False,
                   "IPAM": {
                           "Driver": "default",
                           "Options": None,
                           "Config":
                           {
                               "Subnet": "172.17.0.0/16",
                               "Gateway": "172.17.0.1"
                           }
                   },
                   "Internal": False,
                   "Attachable": False,
                   "Ingress": False,
                   "ConfigFrom": {
                       "Network": ""
                   },
                   "ConfigOnly": False,
                   "Containers": {
                       "199c590e8f13477": {
                           "Name": "al_dpath",
                           "EndpointID": "3042bbe16160a63b7",
                           "MacAddress": "02:34:0a:11:10:22",
                           "IPv4Address": "172.17.0.2/16",
                           "IPv6Address": ""
                       }
                   },
                   "Options": {
                       "com.docker.network.bridge.default_bridge": "true",
                       "com.docker.network.bridge.enable_icc": "true",
                       "com.docker.network.bridge.enable_ip_masquerade": "true",
                       "com.docker.network.bridge.host_binding_ipv4": "0.0.0.0",
                       "com.docker.network.bridge.name": "docker0",
                       "com.docker.network.driver.mtu": "1500"
                   },
                   "Labels": {}
                   }

        self.specs2Pairs = ((["*", re.compile("[A-Z][a-z\\d]*$")],
                             ("IPAM/Driver", "IPAM/Options", "IPAM/Config", "ConfigFrom/Network")),
                            (["**", re.compile("[A-Z][a-z\\d]*$")],
                             ("Name", "Id", "Created", "Scope", "Driver", "Internal", "Attachable",
                                "Ingress", "Containers", "Options", "Labels", "IPAM/Driver", "IPAM/Options",
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
                            (["**", re.compile(r"[A-Z][a-z\d]*$")],
                             ("Name", "Id", "Created", "Scope", "Driver", "Internal", "Attachable",
                                "Ingress", "Containers", "Options", "Labels", "IPAM/Driver", "IPAM/Options",
                                "IPAM/Config", "IPAM/Config/Subnet", "IPAM/Config/Gateway",
                                "ConfigFrom/Network", "Containers/199c590e8f13477/Name")),
                            (["**", re.compile(r"[A-Z][A-Za-z\d]*Address$")],
                             ("Containers/199c590e8f13477/MacAddress", "Containers/199c590e8f13477/IPv4Address",
                                "Containers/199c590e8f13477/IPv6Address")),
                            (["**", re.compile(r"[A-Za-z]+\d+$")], ("EnableIPv6",)),
                            (["**", re.compile(r"\d+[.]\d+")], None)
                            )

        self.specs3Pairs = (("**/{^[A-Za-z]{2}$}", ("Id",)),
                            ("{^[A-Za-z]{2}$}", ("Id",)),
                            (re.compile("^[A-Za-z]{2}$"), ("Id",)),
                            ("*/{[A-Z][A-Za-z\\d]*$}", ("IPAM/Driver", "IPAM/Options", "IPAM/Config", "ConfigFrom/Network")),
                            ("**/{[A-Z][A-Za-z\\d]*\\d$}", ("EnableIPv6",)),
                            ("**/{[A-Z][A-Za-z\\d]*Address$}", ("Containers/199c590e8f13477/MacAddress",
                                                                "Containers/199c590e8f13477/IPv4Address",
                                                                "Containers/199c590e8f13477/IPv6Address")),

                            # repeated intentionally using raw strings rather than '\\' escapes

                            (r"**/{[A-Z][A-Za-z\d]*\d$}", ("EnableIPv6",)),
                            (r"**/{[A-Z][A-Za-z\d]*Address$}", ("Containers/199c590e8f13477/MacAddress",
                                                                "Containers/199c590e8f13477/IPv4Address",
                                                                "Containers/199c590e8f13477/IPv6Address")),
                            )
        return self


class TestSearch(unittest.TestCase):

    def test1(self):
        print("Entered test1", file=sys.stderr)
        dicts = SampleDicts().build()
        dict1 = dicts.d1
        specs = dicts.specs1Pairs
        for (spec, expect) in specs:
            print(f"Spec={spec}", file=sys.stderr)
            found = set()
            for (path, value) in DP.search(dict1, spec, yielded=True):
                print(f"\tpath={path}\tv={value}\n\texpected={expect}",
                      file=sys.stderr)
                if path is None:
                    assert expect is None
                else:
                    found.add(path)
                    assert (path in expect)
            if expect is not None:
                diff = found ^ set(expect)
                if len(diff) != 0:
                    print(f"Error\t{found=}\n\t{expect=}", file=sys.stderr)
                    print(f"Symmetric Difference : {diff}", file=sys.stderr)
                    assert False
            else:
                assert len(found) == 0    


    def test2(self):
        print("Entered test2", file=sys.stderr)
        print(f"Test for filtering for int values", file=sys.stderr)

        def afilter(x):
            if isinstance(x, int):
                return True
            return False

        dicts = SampleDicts().build()
        dict1 = dicts.d1
        specs = dicts.specs1
        for spec, expected in ( (s[0],s[3]) for s in specs):
            print(f"Spec={spec}, Key={expected}", file=sys.stderr)
            result = set()
            for ret in DP.search(dict1, spec, yielded=True, afilter=afilter):
                print(f"\tret={ret}", file=sys.stderr)
                result.add(ret[1])
                assert isinstance(ret[1], int)
            assert result == expected

    def test3(self):
        print("Entered test3", file=sys.stderr)
        dicts = SampleDicts().build()
        dict1 = dicts.d2
        specs = dicts.specs2Pairs
        for (spec, expect) in specs:
            print(f"Spec={spec}", file=sys.stderr)
            found = set()
            for (path, value) in DP.search(dict1, spec, yielded=True):
                print(f"\tpath={path}\tv={value}", file=sys.stderr)
                if path is None:
                    assert expect is None
                else:
                    found.add(path)
                    assert (path in expect)
            if expect is not None:
                diff = found ^ set(expect)
                if len(diff) != 0:
                    print(f"Error\t{found=}\n\t{expect=}", file=sys.stderr)
                    print(f"Symmetric Difference : {diff}", file=sys.stderr)
                    assert False
            else:
                assert len(found) == 0

    def test4(self):
        print("Entered test4", file=sys.stderr)
        dicts = SampleDicts().build()
        dict1 = dicts.d2
        specs = dicts.specs3Pairs
        for (spec, expect) in specs:
            print(f"Spec={spec}", file=sys.stderr)
            found = set()
            for (path, value) in DP.search(dict1, spec, yielded=True):
                print(f"\tpath={path}\tv={value}", file=sys.stderr)
                if path is None:
                    assert expect is None
                else:
                    found.add(path)
                    assert (path in expect)
            if expect is not None:
                diff = found ^ set(expect)
                if len(diff) != 0:
                    print(f"Error\t{found=}\n\t{expect=}", file=sys.stderr)
                    print(f"Symmetric Difference : {diff}", file=sys.stderr)
                    assert False
            else:
                assert len(found) == 0

    def test5(self):
        print("Entered test5 -- re.error::", file=sys.stderr)
        dicts = SampleDicts().build()
        dict1 = dicts.d2
        specs = (("/**/{zz)bad}", "ERROR"),
                 ("{zz)bad}/yyy", "ERROR"),
                 ("**/{zz)bad}/yyy", "ERROR"),
                 ("**/{zz)bad}/yyy/.*", "ERROR"),
                 (123, "OTHERERROR"))

        for (spec, expect) in specs:
            print(f"Spec={spec}", file=sys.stderr)
            try:
                for (path, value) in DP.search(dict1, spec, yielded=True):
                    print(f"\tpath={path}\tv={value}", file=sys.stderr)
                    assert expect not in ("ERROR", "OTHERERROR")
            except InvalidRegex as errExpected:
                print(f"Expected error:{errExpected}", file=sys.stderr)
                assert expect == "ERROR"
            except Exception as errExpected:
                print(f"Expected error:{errExpected}", file=sys.stderr)
                assert expect == "OTHERERROR"


class TestGet(unittest.TestCase):

    def test1(self):
        print("Entered test1", file=sys.stderr)

        dicts = SampleDicts().build()
        dict1 = dicts.d1
        specs = dicts.specs1GetPairs
        for (spec, expect) in specs:
            print(f"Spec={spec}", file=sys.stderr)
            try:
                ret = DP.get(dict1, spec, default=("*NONE*",))
                print(f"\tret={ret}", file=sys.stderr)
                assert (ret == expect)
            except ValueError as err:
                print("\t get fails:", err, type(err), file=sys.stderr)
                assert (expect == "*FAIL*")


class TestDelete(unittest.TestCase):
    def test1(self):
        print("This is test1", file=sys.stderr)
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


class TestView(unittest.TestCase):
    def test1(self):
        print("Entered test1", file=sys.stderr)

        dicts = SampleDicts().build()
        dict1 = dicts.d1
        specs = dicts.specs1
        for spec in specs:
            for ret in DP.segments.view(dict1, spec[0]):
                print(f"\tview spec:{spec} returns:{ret}", file=sys.stderr)
                assert ret == spec[1]


class TestMatch(unittest.TestCase):
    def test1(self):
        print("Entered test1", file=sys.stderr)

        dicts = SampleDicts().build()
        dict1 = dicts.d1
        specs = dicts.specs1
        for spec in specs:
            ret = DP.segments.match(dict1, spec[0])
            print(f"\tmatch spec:{spec} returns:{ret}", file=sys.stderr)
            assert ret == spec[2]
