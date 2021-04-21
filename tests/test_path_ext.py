#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
#
# (C) Alain Lichnewsky, 2021
#
import os
import sys
import re


import unittest
from hypothesis import given, assume, settings, HealthCheck
import hypothesis.strategies as st

from dpath import options
import dpath.segments as api

# enables to modify some globals
MAX_SAMPLES = None
if __name__ == "__main__":
    if "-v" in sys.argv:
        MAX_SAMPLES = 50


settings.register_profile("default", suppress_health_check=(HealthCheck.too_slow,))
settings.load_profile(os.getenv(u'HYPOTHESIS_PROFILE', 'default'))
MAX_LEAVES = 3
if MAX_SAMPLES is None:
    MAX_SAMPLES = 1000
ALPHABET = ('A', 'B', 'C', ' ')
ALPHABETK = ('a', 'b', 'c', '-')

random_key_int = st.integers(0, 100)
random_key_str = st.text(alphabet=ALPHABETK, min_size=2)
random_key = random_key_str | random_key_int
random_segments = st.lists(random_key, max_size=4)
random_leaf = random_key_int | st.text(alphabet=ALPHABET,min_size=2)


if options.ALLOW_EMPTY_STRING_KEYS:
    random_thing = st.recursive(
        random_leaf,
        lambda children: (st.lists(children,max_size=3)
                          | st.dictionaries(st.binary(max_size=5)
                          | st.text(alphabet=ALPHABET), children)),
        max_leaves=MAX_LEAVES)
else:
    random_thing = st.recursive(
        random_leaf,
        lambda children: (st.lists(children,max_size=3) 
                          | st.dictionaries(st.binary(min_size=1,max_size=5)
                          | st.text(min_size=1, alphabet=ALPHABET),
                            children)),
        max_leaves=MAX_LEAVES)

random_node = random_thing.filter(lambda thing: isinstance(thing, (list, dict)))

if options.ALLOW_EMPTY_STRING_KEYS:
    random_mutable_thing = st.recursive(
        random_leaf,
        lambda children: (st.lists(children,max_size=3) | st.text(alphabet=ALPHABET),
                          children), max_leaves=MAX_LEAVES)
else:
    random_mutable_thing = st.recursive(
        random_leaf,
        lambda children: (st.lists(children,max_size=3)
                          | st.dictionaries( st.text(alphabet=ALPHABET, min_size=1),
                          children)),
        max_leaves=MAX_LEAVES)


random_mutable_node = random_mutable_thing.filter(lambda thing: isinstance(thing, (list, dict)))


@st.composite
def mutate(draw, segment):
    # Convert number segments.
    segment = api.int_str(segment)

    # Infer the type constructor for the result.
    kind = type(segment)

    # Produce a valid kind conversion for our wildcards.
    if isinstance(segment, bytes):
        def to_kind(v):
            try:
                return bytes(v, 'utf-8')
            except:
                return kind(v)
    else:
        def to_kind(v):
            return kind(v)

    # Convert to an list of single values.
    converted = []
    for i in range(len(segment)):
        # This carefully constructed nonsense to get a single value
        # is necessary to work around limitations in the bytes type
        # iteration returning integers instead of byte strings of
        # length 1.
        c = segment[i:i + 1]

        # Check for values that need to be escaped.
        if c in tuple(map(to_kind, ('*', '?', '[', ']'))):
            c = to_kind('[') + c + to_kind(']')

        converted.append(c)

    # Start with a non-mutated result.
    result = converted

    # 50/50 chance we will attempt any mutation.
    change = draw(st.sampled_from((True, False)))
    if change:
        result = []

        # For every value in segment maybe mutate, maybe not.
        for c in converted:
            # If the length isn't 1 then, we know this value is already
            # an escaped special character. We will not mutate these.
            if len(c) != 1:
                result.append(c)
            else:
                result.append(draw(st.sampled_from((c, to_kind('?'), to_kind('*')))))

    combined = kind().join(result)

    # If we by chance produce the star-star result, then just revert
    # back to the original converted segment. This is not the mutation
    # you are looking for.
    if combined == to_kind('**'):
        combined = kind().join(converted)

    return combined


@st.composite
def random_segments_with_glob(draw):
    segments = draw(random_segments)
    glob = list(map(lambda x: draw(mutate(x)), segments))

    # 50/50 chance we will attempt to add a star-star to the glob.
    use_ss = draw(st.sampled_from((True, False)))
    if use_ss:
        # Decide if we are inserting a new segment or replacing a range.
        insert_ss = draw(st.sampled_from((True, False)))
        if insert_ss:
            index = draw(st.integers(0, len(glob)))
            glob.insert(index, '**')
        else:
            start = draw(st.integers(0, len(glob)))
            stop = draw(st.integers(start, len(glob)))
            glob[start:stop] = ['**']

    return (segments, glob)

    
rex_translate = re.compile("([*?])")    
@st.composite
def random_segments_with_re_glob(draw):
    (segments, glob) = draw(random_segments_with_glob())
    glob1 = []
    for g in glob:
        if g == "**" or not isinstance(g, str):
            glob1.append(g)
            continue
        try:
            g0 = rex_translate.sub(".\\1",g)
            g1 = re.compile("^" + g0 + "$")
        except Exception:
            print(f"Unable to re.compile:({type(g)}){g}", file=sys.stderr)
            g1 = g
        glob1.append(g1)

    return (segments, glob1)


@st.composite
def random_segments_with_nonmatching_glob(draw):
    (segments, glob) = draw(random_segments_with_glob())

    # Generate a segment that is not in segments.
    invalid = draw(random_key.filter(lambda x: x not in segments and x not in ('*', '**')))

    # Do we just have a star-star glob? It matches everything, so we
    # need to replace it entirely.
    if len(glob) == 1 and glob[0] == '**':
        glob = [invalid]
    # Do we have a star glob and only one segment? It matches anything
    # in the segment, so we need to replace it entirely.
    elif len(glob) == 1 and glob[0] == '*' and len(segments) == 1:
        glob = [invalid]
    # Otherwise we can add something we know isn't in the segments to
    # the glob.
    else:
        index = draw(st.integers(0, len(glob)))
        glob.insert(index, invalid)

    return (segments, glob)

@st.composite
def random_segments_with_nonmatching_re_glob(draw):
    (segments, glob) = draw(random_segments_with_nonmatching_glob())
    glob1 = []
    for g in glob:
        if g == "**" or not isinstance(g, str):
            glob1.append(g)
            continue
        try:
            g0 = rex_translate.sub(".\\1",g)    
            g1 = re.compile("^"+g0+"$")
        except Exception:
            print(f"(non-matching):Unable to re.compile:({type(g)}){g}", file=sys.stderr )
            g1 = g
        glob1.append(g1)
            
    return (segments, glob1)

def setup():
    # Allow empty strings in segments.
    options.ALLOW_EMPTY_STRING_KEYS = True


def teardown():
    # Revert back to default.
    options.ALLOW_EMPTY_STRING_KEYS = False


#
# Run under unittest
#
class TestEncoding(unittest.TestCase):
    DO_DEBUG_PRINT = False

    @settings(max_examples=MAX_SAMPLES)
    @given(random_node)
    def test_kvs(self, node):
        '''
        Given a node, kvs should produce a key that when used to extract
        from the node renders the exact same value given.
        '''
        for k, v in api.kvs(node):
            assert node[k] is v


    @settings(max_examples=MAX_SAMPLES)        
    @given(thing=random_thing )
    def test_fold(self, thing):
        '''
        Given a thing, count paths with fold.
        '''
        def f(o, p, a):
            a[0] += 1

        [count] = api.fold(thing, f, [0])
        assert count == len(tuple(api.walk(thing)))


    @settings(max_examples=MAX_SAMPLES)        
    @given(random_segments_with_glob())
    def test_match(self, pair):
        '''
        Given segments and a known good glob, match should be True.
        '''
        (segments, glob) = pair
        assert api.match(segments, glob) is True
        if TestEncoding.DO_DEBUG_PRINT:
            print(f"api.match: segments:{segments} , glob:{glob}", file=sys.stderr)
        
    @settings(max_examples=MAX_SAMPLES)        
    @given(random_segments_with_re_glob())
    def test_match_re(self, pair):
        '''
        Given segments and a known good glob, match should be True.
        '''
        (segments, glob) = pair
        assert api.match(segments, glob) is True
        if TestEncoding.DO_DEBUG_PRINT:
            print(f"api.match: segments:{segments} , glob:{glob}", file=sys.stderr)
        
    
    @given(random_segments_with_nonmatching_re_glob())
    def test_match_nonmatching_re(self, pair):
        '''
        Given segments and a known bad glob, match should be False.
        '''
        (segments, glob) = pair
        assert api.match(segments, glob) is False
        if TestEncoding.DO_DEBUG_PRINT:
            print(f"api.match:non match OK: segments:{segments} , glob:{glob}", file=sys.stderr)


if __name__ == "__main__":
    if "-h" in sys.argv:
        description = """\
This may run either under tox or standalone. When standalone
flags -h and -v are recognized, other flags are dealt with by unittest.main
and may select test cases.

Flags:
    -h print this help and quit
    -v print information messages on stderr; also reduces MAX_SAMPLES to 50
"""
        print(description)
        sys.exit(0)

    if "-v" in sys.argv:
        sys.argv = [x for x in sys.argv if x != "-v"]
        TestEncoding.DO_DEBUG_PRINT = True
        print("Set verbose mode", file=sys.stderr)
        
    unittest.main()
