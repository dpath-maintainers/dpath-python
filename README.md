dpath-python
============

A python library for accessing and searching dictionaries via /slashed/paths ala xpath

Basically it lets you glob over a dictionary as if it were a filesystem.

Examples
========

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

... You can also use the globbing syntax to set items, create items, etc. See the help for new() and set():

    >>> help(dpath.util.set)
    Help on function set in module dpath.util:

    set(obj, glob, value)
	Given a path glob, set all existing elements in the document
	to the given value. Returns the number of elements changed.

    >>> help(dpath.util.new)
    Help on function new in module dpath.util:

    new(obj, path, value)
	Set the element at the terminus of path to value, and create
	it if it does not exist (as opposed to 'set' that can only
	change existing keys).

	path will NOT be treated like a glob. If it has globbing
	characters in it, they will become part of the resulting
	keys

Handy!

Also, check out dpath.util.merge. The python dict update() method is great and all but doesn't handle merging dictionaries deeply. This one does.

    >>> help(dpath.util.merge)
    Help on function merge in module dpath.util:

    merge(dst, src)
	Merge source into destination. Like dict.update() but performs
	deep merging.

