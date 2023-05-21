# -*- coding: utf-8 -*-
# -*- mode: Python -*-
#
# (C) Alain Lichnewsky, 2023
#
# These classes are used to simplify testing code  in test_regexp_exts_simple.py.
#
# They allow:
#      1) to iterate over a sequence of test-cases specifying:
#           a) a glob expression describing a list of paths
#           b) a list of expected results
#      2) apply a function on each test-case
#      3) check that all outputs are withing the specified results and that all
#         expected results have  been produced at least once
#
# The currently implemented classes: do not check the order of the output results,
# or the multiplicity (beyond "at least once")
#
# Examples are shown in file test_regexp_ext_simple.py.
# ------------------------------------------------------------------------

import sys

from typing import Sequence, Union, Dict
from pprint import PrettyPrinter

# single point of parametrization of output stream
_print_file = sys.stderr


def show(*posArgs, **keyArgs):
    print(*posArgs, file=_print_file, **keyArgs)


class Loop:
    """ Given a dict and a specification table (containing a path/glob specification
        and a list of expected result), apply a function to each spec and verify the
        result wrt.  the expected result.

        The run method checks that all results are in the expected list and that each
        expected result has been produced once. No consideration is given to multiplicity and order.
    """
    def __init__(self, data: Union[Sequence, Dict], specs: Sequence):
        """ Defines the data dict/sequence to which functions are applied, and
            a sequence of test cases specified with tuples of an input and a sequence of outputs.

        Args:
            data (Union[Sequence, Dict]): the dict to which dpath functions are applied
            specs (Sequence): Each entry is a tuple: (test specification, output)
        """
        self.data = data
        self.specs = specs
        self.verbose = False
        self.indent = 12
        self.pretty = PrettyPrinter(indent=self.indent, width=120)
        self.pp = lambda x: x

    def setVerbose(self, v=True):
        """set the verbosity level, if true all tests cases and results are listed

        Args:
            v (bool, optional):Defaults to  True

        Returns: self, for chaining methods
        """
        self.verbose = v
        return self

    def setPrettyPrint(self):
        """Set pretty printing mode

        Returns: self, for chaining methods
        """
        self.pp = self._pretty
        return self

    def _pretty(self, x):
        """Internal method for returning :
            - if PrettyPrint is set: a pretty printed/indented result
            - otherwise : the unchanged input

        Args:
            x (Any): object which can be processed by Python's pretty printer

        Returns: a pretty string
        """
        def do_NL(x):
            if "\n" in x:
                return "\n" + " " * self.indent + x
            else:
                return x

        return do_NL(self.pretty.pformat(x))

    def _validate_collect(self, result, expected, found):
        """ (internal) Checks that the result produced is in the 'expected' field of the test
            specification table. No exception is expected, but the user may have special
            result strings to denote exception. (see examples in test_regexp_ext_simple)

            The result is collected for later determination of missing results wrt. expected.

        Args:
            result : the result to be tested or an Exception instance
            expected : sequence of expected results
            found ( set): set used to collect results
        """
        if result is None:
            assert expected is None
        elif expected is None:
            show(f"Error: Expected result: None, result={result}")
            assert result is None
        else:
            # this simplifies specs tables when a single output is expected
            if isinstance(expected, (dict, bool, str)):
                expected = (expected,)
            assert result in expected
            found.append(result)

    def _validate_collection(self, expected, found, spec, specCount):
        """ (internal)  Checks that the found sequence covers all expected values.
        Args:
            expected (Sequence): expected results
            found ( Set): observed results
            spec (Sequence): dpath parameter (Glob)
            specCount (int): position in specification table, printed to facilitate identification
                             of diagnostics.
        """
        if expected is not None:
            if isinstance(expected, (dict, bool, str)):
                expected = (expected,)

            # compute difference between found and expected
            diff = [x for x in expected if (x not in found)]
            if len(found) == 0:
                found = "None"

            # tell the user
            if len(diff) != 0:
                if not self.verbose:
                    show(f"\t{specCount:2} spec:{spec}")
                show(f"Error\t(Sets) Found:{self.pp(found)}\n\tExpected:{self.pp(expected)}")
                show(f"Expected values missing : {self.pp(diff)}")
                assert len(diff) == 0
        else:
            if len(found) > 0:
                if not self.verbose:
                    show(f"\t{specCount:2} spec:{self.pp(spec)},\n\t expected={self.pp(expected)},\n\tself.pp(found)")
                assert len(found) == 0

    def run(self, func):
        """For each tuple in the specification table, apply function func with
            arguments (data, specification) and check that the result is valid.

            If verbose set, outputs test case and sequence of results.

            The set of results of function application is collected and analyzed.

        Args:
            func (data, spec) -> result: function called with arguments data and test case
                specification, returns result to be monitored.
        """
        specCount = 0
        for (spec, expected) in self.specs:
            specCount += 1

            if isinstance(expected, str):
                expected = (expected,)

            if self.verbose:
                show(f"\t{specCount:2} spec:{self.pp(spec)},\t expected={self.pp(expected)}")

            found = []
            for result, value in func(self.data, spec):
                if self.verbose:
                    show(f"\t\tpath:{result}\tvalue:{self.pp(value)}\texpected:{self.pp(expected)}")

                self._validate_collect(result, expected, found)

            self._validate_collection(expected, found, spec, specCount)
