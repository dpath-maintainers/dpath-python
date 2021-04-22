#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: Python -*-
#
from dpath import options
from hypothesis import given, assume, settings, HealthCheck
import dpath.segments as api
import hypothesis.strategies as st


import unittest
import os
import sys

# enables to modify some globals
MAX_SAMPLES = None
if __name__ == "__main__":
    if "-v" in sys.argv:
        MAX_SAMPLES = 30
        MAX_LEAVES = 20

settings.register_profile("default", suppress_health_check=(HealthCheck.too_slow,))
settings.load_profile(os.getenv(u'HYPOTHESIS_PROFILE', 'default'))
if MAX_SAMPLES is None:
    MAX_LEAVES = 50
    MAX_SAMPLES = 100


random_key_int = st.integers(0, 1000)
random_key_str = st.binary() | st.text()
random_key = random_key_str | random_key_int
random_segments = st.lists(random_key)
random_leaf = st.integers() | st.floats() | st.booleans() | st.binary() | st.text() | st.none()

if options.ALLOW_EMPTY_STRING_KEYS:
    random_thing = st.recursive(
        random_leaf,
        lambda children: (st.lists(children) | st.tuples(children)
                          | st.dictionaries(st.binary() | st.text(), children)),
        max_leaves=MAX_LEAVES)
else:
    random_thing = st.recursive(
        random_leaf,
        lambda children: (st.lists(children) | st.tuples(children)
                          | st.dictionaries(st.binary(min_size=1) | st.text(min_size=1),
                                            children)),
        max_leaves=MAX_LEAVES)

random_node = random_thing.filter(lambda thing: isinstance(thing, (list, tuple, dict)))

if options.ALLOW_EMPTY_STRING_KEYS:
    random_mutable_thing = st.recursive(
        random_leaf,
        lambda children: st.lists(children) | st.dictionaries(st.binary() | st.text(),
                                                              children),
        max_leaves=MAX_LEAVES)
else:
    random_mutable_thing = st.recursive(
        random_leaf,
        lambda children: (st.lists(children)
                          | st.dictionaries(st.binary(min_size=1) | st.text(min_size=1),
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
def random_walk(draw):
    node = draw(random_mutable_node)
    found = tuple(api.walk(node))
    assume(len(found) > 0)
    return (node, draw(st.sampled_from(found)))


@st.composite
def random_leaves(draw):
    node = draw(random_mutable_node)
    found = tuple(api.leaves(node))
    assume(len(found) > 0)
    return (node, draw(st.sampled_from(found)))


def setup():
    # Allow empty strings in segments.
    options.ALLOW_EMPTY_STRING_KEYS = True


def teardown():
    # Revert back to default.
    options.ALLOW_EMPTY_STRING_KEYS = False

#
# Run under unittest
#
class TestSegments(unittest.TestCase):
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
    @given(random_leaf)
    def test_leaf_with_leaf(self, leaf):
        '''
        Given a leaf, leaf should return True.
        '''
        assert api.leaf(leaf) is True


    @settings(max_examples=MAX_SAMPLES)
    @given(random_node)
    def test_leaf_with_node(self, node):
        '''
        Given a node, leaf should return False.
        '''
        assert api.leaf(node) is False


    @settings(max_examples=MAX_SAMPLES)
    @given(random_thing)
    def test_walk(self, thing):
        '''
        Given a thing to walk, walk should yield key, value pairs where key
        is a tuple of non-zero length.
        '''
        for k, v in api.walk(thing):
            assert isinstance(k, tuple)
            assert len(k) > 0


    @settings(max_examples=MAX_SAMPLES)
    @given(random_node)
    def test_get(self, node):
        '''
        Given a node, get should return the exact value given a key for all
        key, value pairs in the node.
        '''
        for k, v in api.walk(node):
            assert api.get(node, k) is v


    @settings(max_examples=MAX_SAMPLES)
    @given(random_node)
    def test_has(self, node):
        '''
        Given a node, has should return True for all paths, False otherwise.
        '''
        for k, v in api.walk(node):
            assert api.has(node, k) is True

            # If we are at a leaf, then we can create a value that isn't
            # present easily.
            if api.leaf(v):
                assert api.has(node, k + (0,)) is False


    @settings(max_examples=MAX_SAMPLES)
    @given(random_segments)
    def test_expand(self, segments):
        '''
        Given segments expand should produce as many results are there were
        segments and the last result should equal the given segments.
        '''
        count = len(segments)
        result = list(api.expand(segments))

        assert count == len(result)

        if count > 0:
            assert segments == result[-1]


    @settings(max_examples=MAX_SAMPLES)
    @given(random_node)
    def test_types(self, node):
        '''
        Given a node, types should yield a tuple of key, type pairs and the
        type indicated should equal the type of the value.
        '''
        for k, v in api.walk(node):
            ts = api.types(node, k)
            ta = ()
            for tk, tt in ts:
                ta += (tk,)
                assert type(api.get(node, ta)) is tt


    @settings(max_examples=MAX_SAMPLES)
    @given(random_node)
    def test_leaves(self, node):
        '''
        Given a node, leaves should yield only leaf key, value pairs.
        '''
        for k, v in api.leaves(node):
            assert api.leafy(v)


    @settings(max_examples=MAX_SAMPLES)
    @given(random_segments_with_glob())
    def test_match(self, pair):
        '''
        Given segments and a known good glob, match should be True.
        '''
        (segments, glob) = pair
        assert api.match(segments, glob) is True


    @settings(max_examples=MAX_SAMPLES)
    @given(random_segments_with_nonmatching_glob())
    def test_match_nonmatching(self, pair):
        '''
        Given segments and a known bad glob, match should be False.
        '''
        print(pair)
        (segments, glob) = pair
        assert api.match(segments, glob) is False


    @settings(max_examples=MAX_SAMPLES)
    @given(walkable=random_walk(), value=random_thing)
    def test_set_walkable(self, walkable, value):
        '''
        Given a walkable location, set should be able to update any value.
        '''
        (node, (segments, found)) = walkable
        api.set(node, segments, value)
        assert api.get(node, segments) is value


    @settings(max_examples=MAX_SAMPLES)
    @given(walkable=random_leaves(),
           kstr=random_key_str,
           kint=random_key_int,
           value=random_thing,
           extension=random_segments)
    def test_set_create_missing(self, walkable, kstr, kint, value, extension):
        '''
        Given a walkable non-leaf, set should be able to create missing
        nodes and set a new value.
        '''
        (node, (segments, found)) = walkable
        assume(api.leaf(found))

        parent_segments = segments[:-1]
        parent = api.get(node, parent_segments)

        if isinstance(parent, list):
            assume(len(parent) < kint)
            destination = parent_segments + (kint,) + tuple(extension)
        elif isinstance(parent, dict):
            assume(kstr not in parent)
            destination = parent_segments + (kstr,) + tuple(extension)
        else:
            raise Exception('mad mad world')

        api.set(node, destination, value)
        assert api.get(node, destination) is value


    @settings(max_examples=MAX_SAMPLES)
    @given(thing=random_thing)
    def test_fold(self, thing):
        '''
        Given a thing, count paths with fold.
        '''
        def f(o, p, a):
            a[0] += 1

        [count] = api.fold(thing, f, [0])
        assert count == len(tuple(api.walk(thing)))


    @settings(max_examples=MAX_SAMPLES)
    @given(walkable=random_walk())
    def test_view(self, walkable):
        '''
        Given a walkable location, view that location.
        '''
        (node, (segments, found)) = walkable
        assume(found == found)  # Hello, nan! We don't want you here.

        view = api.view(node, segments)
        ag1 = api.get(view, segments)
        ag2 = api.get(node, segments)
        if ag1 != ag2:
            print("Error for segments={segments}\n\tag1={ag1}\n\tag2={ag2}")
        assert ag1 == ag2

        
if __name__ == "__main__":
    if "-h" in sys.argv:
        description = """\
This may run either under tox or standalone. When standalone
flags -h and -v are recognized, other flags are dealt with by unittest.main
and may select test cases.

Flags:
    -h print this help and quit
    -v print information messages on stderr; also reduces MAX_SAMPLES to 30

Autonomous CLI syntax:
    python3 [-h] [-v] [TestSegments[.<testname>]]
   
    e.g.     python3 TestSegments.test_match_re
"""
        print(description)
        sys.exit(0)

    if "-v" in sys.argv:
        sys.argv = [x for x in sys.argv if x != "-v"]
        TestSegments.DO_DEBUG_PRINT = True
        sys.stderr.write("Set verbose mode\n")

    unittest.main()
