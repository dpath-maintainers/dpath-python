#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
#
# (C) Alain Lichnewsky, 2022
#
#     Test many functionalities that use path specifications for support of extended specs with re.regex
#
import sys
import re

from copy import copy

import unittest
import dpath as DP


def _sprint(*args, **kwdargs):
    print(*args, **kwdargs, file=sys.stderr)


# check that how the options have been set
_sprint(f"At entry in test_path_ext DPATH_ACCEPT_RE_REGEXP = {DP.options.DPATH_ACCEPT_RE_REGEXP}")

if not DP.options.DPATH_ACCEPT_RE_REGEXP:
    _sprint("This test requires DPATH_ACCEPT_RE_REGEXP = True")
    DP.options.DPATH_ACCEPT_RE_REGEXP = True  # enable re.regexp support in path expr.


# one class per function to be tested
class SampleDicts():
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

    specs1 = ([re.compile(".*")],
              [re.compile("[a-z]+$")],
              ["*", re.compile(".*")],
              ["*", "*", re.compile(".*")],
              ["*", re.compile("[a-z]+\\d+$")],
              ["*", re.compile("[a-z]+[.][a-z]+$")],
              ["**", re.compile(".*")],
              ["**", re.compile("[a-z]+\\d+$")],
              ["**", re.compile("[a-z]+[.][a-z]+$")]
              )

    specs1Pairs = (([re.compile(".*")], ("a001",)),
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
                    ("a001/b2/c1.2/d.dd", "a001/b2/c1.2/e.ee")))

    specs1GetPairs = (([re.compile(".*")], {'b2': {'c1.2': {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}}}),
                      ([re.compile("[a-z]+$")], ('*NONE*',)),
                      (["*", re.compile(".*")], {'c1.2': {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}}),
                      (["*", "*", re.compile(".*")], {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}),
                      (["*", re.compile("[a-z]+\\d+$")], {'c1.2': {'d.dd': 0, 'e.ee': 1, 'f.f0': 2}}),
                      (["*", re.compile("[a-z]+[.][a-z]+$")], ('*NONE*',)),
                      (["**", re.compile(".*")], "*FAIL*"),
                      (["**", re.compile("[a-z]+\\d+$")], "*FAIL*"),
                      (["**", re.compile("[a-z]+[.][a-z]+$")], "*FAIL*"))

    d2 = {"Name": "bridge",
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
              "Network": ""},
          "ConfigOnly": False,
          "Containers": {
              "199c590e8f13477": {
                  "Name": "al_dpath",
                  "EndpointID": "3042bbe16160a63b7",
                  "MacAddress": "02:34:0a:11:10:22",
                  "IPv4Address": "172.17.0.2/16",
                  "IPv6Address": ""}},
          "Options": {
              "com.docker.network.bridge.default_bridge": "true",
              "com.docker.network.bridge.enable_icc": "true",
              "com.docker.network.bridge.enable_ip_masquerade": "true",
              "com.docker.network.bridge.host_binding_ipv4": "0.0.0.0",
              "com.docker.network.bridge.name": "docker0",
              "com.docker.network.driver.mtu": "1500"},
          "Labels": {}}

    specs2Pairs = ((["*", re.compile("[A-Z][a-z\\d]*$")],
                    ("IPAM/Driver", "IPAM/Options", "IPAM/Config", "ConfigFrom/Network")),
                   (["**", re.compile("[A-Z][a-z\\d]*$")],
                    ("Name", "Id", "Created", "Scope", "Driver", "Internal", "Attachable",
                     "Ingress", "Containers", "Options", "Labels", "IPAM/Driver", "IPAM/Options",
                     "IPAM/Config", "IPAM/Config/Subnet", "IPAM/Config/Gateway",
                     "ConfigFrom/Network", "Containers/199c590e8f13477/Name",
                     "Containers/199c590e8f13477/MacAddress")),
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
                     "ConfigFrom/Network", "Containers/199c590e8f13477/Name",
                     "Containers/199c590e8f13477/MacAddress")),
                   (["**", re.compile(r"[A-Z][A-Za-z\d]*Address$")],
                    ("Containers/199c590e8f13477/MacAddress", "Containers/199c590e8f13477/IPv4Address",
                     "Containers/199c590e8f13477/IPv6Address")),
                   (["**", re.compile(r"[A-Za-z]+\d+$")], ("EnableIPv6",)),
                   (["**", re.compile(r"\d+[.]\d+")], None))

    specs3Pairs = (("**/{[^A-Za-z]{2}$}", ("Id",)),
                   ("*/{[A-Z][A-Za-z\\d]*$}", ("Name", "Id", "Created", "Scope", "Driver", "Internal",
                                               "Attachable", "Ingress", "Containers", "Options", "Labels",
                                               "IPAM/Driver", "IPAM/Options", "IPAM/Config", "IPAM/Config/Subnet",
                                               "IPAM/Config/Gateway", "ConfigFrom/Network", "Containers/199c590e8f13477/Name",
                                               "Containers/199c590e8f13477/MacAddress")),
                   ("**/{[A-Z][A-Za-z\\d]*\\d$}", ("EnableIPv6",)),
                   ("**/{[A-Z][A-Za-z\\d]*Address$}", ("Containers/199c590e8f13477/MacAddress",
                                                       "Containers/199c590e8f13477/IPv4Address",
                                                       "Containers/199c590e8f13477/IPv6Address")),

                   # repeated intentionally using raw strings rather than '\\' escapes

                   (r"**/{[A-Z][A-Za-z\d]*\d$}", ("EnableIPv6",)),
                   (r"**/{[A-Z][A-Za-z\d]*Address$}", ("Containers/199c590e8f13477/MacAddress",
                                                       "Containers/199c590e8f13477/IPv4Address",
                                                       "Containers/199c590e8f13477/IPv6Address")))


class TestSearch(unittest.TestCase):

    def test1(self):
        _sprint("Entered test1")
        dict1 = SampleDicts.d1
        specs = SampleDicts.specs1Pairs
        for (spec, expect) in specs:
            _sprint(f"Spec={spec}")
            for (path, value) in DP.search(dict1, spec, yielded=True):
                _sprint(f"\tpath={path}\tv={value}\n\texpected={expect}")
                if path is None:
                    assert expect is None
                else:
                    assert (path in expect)
            _sprint("\n")

    def test2(self):
        _sprint("Entered test2")

        def afilter(x):
            # _sprint(f"In afilter x = {x}({type(x)})")
            if isinstance(x, int):
                return True
            return False

        dict1 = SampleDicts.d1
        specs = SampleDicts.specs1
        for spec in specs:
            _sprint(f"Spec={spec}")
            for ret in DP.search(dict1, spec, yielded=True, afilter=afilter):
                _sprint(f"\tret={ret}")
                assert (isinstance(ret[1], int))

    def test3(self):
        _sprint("Entered test3")

        dict1 = SampleDicts.d2
        specs = SampleDicts.specs2Pairs
        for (spec, expect) in specs:
            _sprint(f"Spec={spec}")
            for (path, value) in DP.search(dict1, spec, yielded=True):
                _sprint(f"\tpath={path}\tv={value}")
                if path is None:
                    assert expect is None
                else:
                    assert (path in expect)

    def test4(self):
        _sprint("Entered test4")

        dict1 = SampleDicts.d2
        specs = SampleDicts.specs3Pairs
        for (spec, expect) in specs:
            _sprint(f"Spec={spec}")
            for (path, value) in DP.search(dict1, spec, yielded=True):
                _sprint(f"\tpath={path}\tv={value}")
                if path is None:
                    assert expect is None
                else:
                    assert (path in expect)


class TestGet(unittest.TestCase):

    def test1(self):
        _sprint("Entered test1")

        dict1 = SampleDicts.d1
        specs = SampleDicts.specs1GetPairs
        for (spec, expect) in specs:
            _sprint(f"Spec={spec}")
            try:
                ret = DP.get(dict1, spec, default=("*NONE*",))
                _sprint(f"\tret={ret}")
                assert (ret == expect)
            except Exception as err:
                x = "expected" if expect == "*FAIL*" else "Error"
                _sprint(f"\t get fails ({x}):", err, type(err))
                assert (expect == "*FAIL*")


class TestDelete(unittest.TestCase):
    def test1(self):
        _sprint("This is test1")
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
            _sprint(f"spec={spec}")
            _sprint(f"Before deletion dict={dict}")
            DP.delete(dict, [spec])
            _sprint(f"After deletion dict={dict}")
            if i == 0:
                assert (dict == {"a0": {"b": 0, }, })
            else:
                assert (dict == {"a": {"b": 0, "12": 0, }})
            i += 1


class TestView(unittest.TestCase):
    def test1(self):
        _sprint("Entered test1")

        dict1 = SampleDicts.d1
        specs = SampleDicts.specs1
        for spec in specs:
            _sprint(f"Spec={spec}")
            for ret in DP.segments.view(dict1, spec):
                _sprint(f"\tview returns:{ret}")


class TestMatch(unittest.TestCase):
    def test1(self):
        _sprint("Entered test1")

        dict1 = SampleDicts.d1
        specs = SampleDicts.specs1
        for spec in specs:
            _sprint(f"Spec={spec}")
            if DP.segments.match(dict1, spec):
                _sprint(f"Spec={spec} matches")
