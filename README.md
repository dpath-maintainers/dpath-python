dpath-python
============

A python library for accessing and searching dictionaries via /slashed/paths ala xpath

Basically it lets you glob over a dictionary as if it were a filesystem. It allows you to specify globs (ala the bash eglob syntax, through some advanced fnmatch.fnmatch magic) to access dictionary elements, and provides some facility for filtering those results.

Automated pylint and nosetest runs are in the AKLabs bamboo, here: http://bamboo.aklabs.net/browse/DPATHPYTHON

sdists are available on pypi: http://pypi.python.org/pypi/dpath

Separators
==========

All of the functions in this library (except 'merge') accept a 'separator' argument, which is the character that should separate path components. The default is '/', but you can set it to whatever you want.

Searching
=========

Suppose we have a dictionary like this:

    x = {
	"a": {
	    "b": {
		"3": 2,
		"43": 30,
		"c": [],
		"d": ['red', 'buggy', 'bumpers'],
	    }
	}
    }


... And we want to say "Give me a new dictionary with the values of all elements in x['a']['b'] where the key is equal to the glob '[cd]'. Okay.

    >>> help(dpath.util.search)
    Help on function search in module dpath.util:

    search(obj, glob, yielded=False)
	Given a path glob, return a dictionary containing all keys
	that matched the given glob.

	If 'yielded' is true, then a dictionary will not be returned.
	Instead tuples will be yielded in the form of (path, value) for
	every element in the document that matched the glob.

... Sounds easy!

    >>> result = dpath.util.search(x, "a/b/[cd]")
    >>> print json.dumps(result, indent=4, sort_keys=True)
    {
	"a": {
	    "b": {
		"c": [],
		"d": [
		    "red",
		    "buggy",
		    "bumpers"
		]
	    }
	}
    }

... Wow that was easy. What if I want to iterate over the results, and not get a merged view?

    >>> for x in dpath.util.search(x, "a/b/[cd]", yielded=True): print x
    ...
    ('a/b/c', [])
    ('a/b/d', ['red', 'buggy', 'bumpers'])

Example: Setting existing keys
==============================

Let's use that same dictionary, and set keys like 'a/b/[cd]' to the value 'Waffles'.

    >>> help(dpath.util.set)
    Help on function set in module dpath.util:

    set(obj, glob, value)
	Given a path glob, set all existing elements in the document
	to the given value. Returns the number of elements changed.

    >>> dpath.util.set(x, 'a/b/[cd]', 'Waffles')
    2
    >>> print json.dumps(x, indent=4, sort_keys=True)
    {
	"a": {
	    "b": {
		"3": 2,
		"43": 30,
		"c": "Waffles",
		"d": "Waffles"
	    }
	}
    }

Example: Adding new keys
========================

Let's make a new key with the path 'a/b/e/f/g', set it to "Roffle". This behaves like 'mkdir -p' in that it makes all the intermediate paths necessary to get to the terminus.

    >>> help(dpath.util.new)
    Help on function new in module dpath.util:

    new(obj, path, value)
	Set the element at the terminus of path to value, and create
	it if it does not exist (as opposed to 'set' that can only
	change existing keys).

	path will NOT be treated like a glob. If it has globbing
	characters in it, they will become part of the resulting
	keys

    >>> dpath.util.new(x, 'a/b/e/f/g', "Roffle")
    >>> print json.dumps(x, indent=4, sort_keys=True)
    {
	"a": {
	    "b": {
		"3": 2,
		"43": 30,
		"c": "Waffles",
		"d": "Waffles",
		"e": {
		    "f": {
			"g": "Roffle"
		    }
		}
	    }
	}
    }

This works the way we expect with lists, as well. If you have a list object and set index 10 of that list object, it will grow the list object with None entries in order to make it big enough:

    >>> dpath.util.new(x, 'a/b/e/f/h', [])
    >>> dpath.util.new(x, 'a/b/e/f/h/13', 'Wow this is a big array, it sure is lonely in here by myself')
    >>> print json.dumps(x, indent=4, sort_keys=True)
    {
	"a": {
	    "b": {
		"3": 2,
		"43": 30,
		"c": "Waffles",
		"d": "Waffles",
		"e": {
		    "f": {
			"g": "Roffle",
			"h": [
			    null,
			    null,
			    null,
			    null,
			    null,
			    null,
			    null,
			    null,
			    null,
			    null,
			    null,
			    null,
			    null,
			    "Wow this is a big array, it sure is lonely in here by myself"
			]
		    }
		}
	    }
	}
    }

Handy!

Example: Merging
================

Also, check out dpath.util.merge. The python dict update() method is great and all but doesn't handle merging dictionaries deeply. This one does.

    >>> help(dpath.util.merge)
    Help on function merge in module dpath.util:

    merge(dst, src, afilter=None, flags=4, _path='')
        Merge source into destination. Like dict.update() but performs
        deep merging.

        flags is an OR'ed combination of MERGE_ADDITIVE, MERGE_REPLACE, or
        MERGE_TYPESAFE.
            * MERGE_ADDITIVE : List objects are combined onto one long
              list (NOT a set). This is the default flag.
            * MERGE_REPLACE : Instead of combining list objects, when
              2 list objects are at an equal depth of merge, replace
              the destination with the source.
            * MERGE_TYPESAFE : When 2 keys at equal levels are of different
              types, raise a TypeError exception. By default, the source
              replaces the destination in this situation.

    >>> y = {'a': {'b': { 'e': {'f': {'h': [None, 0, 1, None, 13, 14]}}}, 'c': 'RoffleWaffles'}}
    >>> print json.dumps(y, indent=4, sort_keys=True)
    {
	"a": {
	    "b": {
		"e": {
		    "f": {
			"h": [
			    null,
			    0,
			    1,
			    null,
			    13,
			    14
			]
		    }
		}
	    },
	    "c": "RoffleWaffles"
	}
    }
    >>> dpath.util.merge(x, y)
    >>> print json.dumps(x, indent=4, sort_keys=True)
    {
	"a": {
	    "b": {
		"3": 2,
		"43": 30,
		"c": "Waffles",
		"d": "Waffles",
		"e": {
		    "f": {
			"g": "Roffle",
			"h": [
			    null,
			    0,
			    1,
			    null,
			    13,
			    14,
			    null,
			    null,
			    null,
			    null,
			    null,
			    null,
			    null,
			    "Wow this is a big array, it sure is lonely in here by myself"
			]
		    }
		}
	    },
	    "c": "RoffleWaffles"
	}
    }

Now that's handy. You shouldn't try to use this as a replacement for the deepcopy method, however - while merge does create new dict and list objects inside the target, the terminus objects (strings and ints) are not copied, they are just re-referenced in the merged object.

Filtering
=========

All of the methods in this library (except new()) support a 'afilter' argument. This can be set to a function that will return True or False to say 'yes include that value in my result set' or 'no don't include it'.

Filtering functions receive every terminus node in a search - e.g., anything that is not a dict or a list, at the very end of the path. For each value, they return True to include that value in the result set, or False to exclude it.

Consider this example. Given the source dictionary, we want to find ALL keys inside it, but we only really want the ones that contain "ffle" in them:

    >>> print json.dumps(x, indent=4, sort_keys=True)
    {
	"a": {
	    "b": {
		"3": 2,
		"43": 30,
		"c": "Waffles",
		"d": "Waffles",
		"e": {
		    "f": {
			"g": "Roffle"
		    }
		}
	    }
	}
    }
    >>> def afilter(x):
    ...     if "ffle" in str(x):
    ...             return True
    ...     return False
    ...
    >>> result = dpath.util.search(x, '**', afilter=afilter)
    >>> print json.dumps(result, indent=4, sort_keys=True)
    {
	"a": {
	    "b": {
		"c": "Waffles",
		"d": "Waffles",
		"e": {
		    "f": {
			"g": "Roffle"
		    }
		}
	    }
	}
    }

Obviously filtering functions can perform more advanced tests (regular expressions, etc etc).

dpath.path : The Undocumented Backend
=====================================

dpath.util is where you want to spend your time: this library has the friendly functions that will understand simple string globs, afilter functions, etc.

dpath.path is the backend pathing library - it is currently undocumented, and not meant to be used directly! It passes around lists of path components instead of string globs, and just generally does things in a way that you (as a frontend user) might not expect. Stay out of it. You have been warned!