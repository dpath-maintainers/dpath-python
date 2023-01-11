dpath-python
============

|PyPI|
|Python Version|
|Build Status|
|Gitter|

A python library for accessing and searching dictionaries via
/slashed/paths ala xpath

Basically it lets you glob over a dictionary as if it were a filesystem.
It allows you to specify globs (ala the bash eglob syntax, through some
advanced fnmatch.fnmatch magic) to access dictionary elements, and
provides some facility for filtering those results.

sdists are available on pypi: http://pypi.python.org/pypi/dpath

Installing
==========

The best way to install dpath is via easy\_install or pip.

::

    easy_install dpath
    pip install dpath

Using Dpath
===========

.. code-block:: python

    import dpath

Separators
==========

All of the functions in this library (except 'merge') accept a
'separator' argument, which is the character that should separate path
components. The default is '/', but you can set it to whatever you want.

Searching
=========

Suppose we have a dictionary like this:

.. code-block:: python

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

... And we want to ask a simple question, like "Get me the value of the
key '43' in the 'b' hash which is in the 'a' hash". That's easy.

.. code-block:: pycon

    >>> help(dpath.get)
    Help on function get in module dpath:

    get(obj, glob, separator='/')
        Given an object which contains only one possible match for the given glob,
        return the value for the leaf matching the given glob.

        If more than one leaf matches the glob, ValueError is raised. If the glob is
        not found, KeyError is raised.

    >>> dpath.get(x, '/a/b/43')
    30

Or you could say "Give me a new dictionary with the values of all
elements in ``x['a']['b']`` where the key is equal to the glob ``'[cd]'``. Okay.

.. code-block:: pycon

    >>> help(dpath.search)
    Help on function search in module dpath:

    search(obj, glob, yielded=False)
    Given a path glob, return a dictionary containing all keys
    that matched the given glob.

    If 'yielded' is true, then a dictionary will not be returned.
    Instead tuples will be yielded in the form of (path, value) for
    every element in the document that matched the glob.

... Sounds easy!

.. code-block:: pycon

    >>> result = dpath.search(x, "a/b/[cd]")
    >>> print(json.dumps(result, indent=4, sort_keys=True))
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

**Note** : Using Python's `re` regular expressions instead of globs is explained
below re_regexp_; defining your own string matcher objects is shown in duck_string_match_ below.

... Wow that was easy. What if I want to iterate over the results, and
not get a merged view?

.. code-block:: pycon

    >>> for x in dpath.search(x, "a/b/[cd]", yielded=True): print(x)
    ...
    ('a/b/c', [])
    ('a/b/d', ['red', 'buggy', 'bumpers'])

... Or what if I want to just get all the values back for the glob? I
don't care about the paths they were found at:

.. code-block:: pycon

    >>> help(dpath.values)
    Help on function values in module dpath:

    values(obj, glob, separator='/', afilter=None, dirs=True)
    Given an object and a path glob, return an array of all values which match
    the glob. The arguments to this function are identical to those of search(),
    and it is primarily a shorthand for a list comprehension over a yielded
    search call.

    >>> dpath.values(x, '/a/b/d/*')
    ['red', 'buggy', 'bumpers']

Example: Setting existing keys
==============================

Let's use that same dictionary, and set keys like 'a/b/[cd]' to the
value 'Waffles'.

.. code-block:: pycon

    >>> help(dpath.set)
    Help on function set in module dpath:

    set(obj, glob, value)
    Given a path glob, set all existing elements in the document
    to the given value. Returns the number of elements changed.

    >>> dpath.set(x, 'a/b/[cd]', 'Waffles')
    2
    >>> print(json.dumps(x, indent=4, sort_keys=True))
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

Let's make a new key with the path 'a/b/e/f/g', set it to "Roffle". This
behaves like 'mkdir -p' in that it makes all the intermediate paths
necessary to get to the terminus.

.. code-block:: pycon

    >>> help(dpath.new)
    Help on function new in module dpath:

    new(obj, path, value)
    Set the element at the terminus of path to value, and create
    it if it does not exist (as opposed to 'set' that can only
    change existing keys).

    path will NOT be treated like a glob. If it has globbing
    characters in it, they will become part of the resulting
    keys

    >>> dpath.new(x, 'a/b/e/f/g', "Roffle")
    >>> print(json.dumps(x, indent=4, sort_keys=True))
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

This works the way we expect with lists, as well. If you have a list
object and set index 10 of that list object, it will grow the list
object with None entries in order to make it big enough:

.. code-block:: pycon

    >>> dpath.new(x, 'a/b/e/f/h', [])
    >>> dpath.new(x, 'a/b/e/f/h/13', 'Wow this is a big array, it sure is lonely in here by myself')
    >>> print(json.dumps(x, indent=4, sort_keys=True))
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

Example: Deleting Existing Keys
===============================

To delete keys in an object, use dpath.delete, which accepts the same globbing syntax as the other methods.

.. code-block:: pycon

    >>> help(dpath.delete)

    delete(obj, glob, separator='/', afilter=None):
        Given a path glob, delete all elements that match the glob.

        Returns the number of deleted objects. Raises PathNotFound if
        no paths are found to delete.

Example: Merging
================

Also, check out dpath.merge. The python dict update() method is
great and all but doesn't handle merging dictionaries deeply. This one
does.

.. code-block:: pycon

    >>> help(dpath.merge)
    Help on function merge in module dpath:

    merge(dst, src, afilter=None, flags=4, _path='')
        Merge source into destination. Like dict.update() but performs
        deep merging.

        flags is an OR'ed combination of MergeType enum members.
            * ADDITIVE : List objects are combined onto one long
              list (NOT a set). This is the default flag.
            * REPLACE : Instead of combining list objects, when
              2 list objects are at an equal depth of merge, replace
              the destination with the source.
            * TYPESAFE : When 2 keys at equal levels are of different
              types, raise a TypeError exception. By default, the source
              replaces the destination in this situation.

    >>> y = {'a': {'b': { 'e': {'f': {'h': [None, 0, 1, None, 13, 14]}}}, 'c': 'RoffleWaffles'}}
    >>> print(json.dumps(y, indent=4, sort_keys=True))
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
    >>> dpath.merge(x, y)
    >>> print(json.dumps(x, indent=4, sort_keys=True))
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

Now that's handy. You shouldn't try to use this as a replacement for the
deepcopy method, however - while merge does create new dict and list
objects inside the target, the terminus objects (strings and ints) are
not copied, they are just re-referenced in the merged object.

Filtering
=========

All of the methods in this library (except new()) support a 'afilter'
argument. This can be set to a function that will return True or False
to say 'yes include that value in my result set' or 'no don't include
it'.

Filtering functions receive every terminus node in a search - e.g.,
anything that is not a dict or a list, at the very end of the path. For
each value, they return True to include that value in the result set, or
False to exclude it.

Consider this example. Given the source dictionary, we want to find ALL
keys inside it, but we only really want the ones that contain "ffle" in
them:

.. code-block:: pycon

    >>> print(json.dumps(x, indent=4, sort_keys=True))
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
    >>> result = dpath.search(x, '**', afilter=afilter)
    >>> print(json.dumps(result, indent=4, sort_keys=True))
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

Obviously filtering functions can perform more advanced tests (regular
expressions, etc etc).

Key Names
=========

By default, dpath only understands dictionary keys that are integers or
strings. String keys must be non-empty. You can change this behavior by
setting a library-wide dpath option:

.. code-block:: python

    import dpath.options
    dpath.options.ALLOW_EMPTY_STRING_KEYS = True

Again, by default, this behavior is OFF, and empty string keys will
result in ``dpath.exceptions.InvalidKeyName`` being thrown.

Separator got you down? Use lists as paths
==========================================

The default behavior in dpath is to assume that the path given is a string, which must be tokenized by splitting at the separator to yield a distinct set of path components against which dictionary keys can be individually glob tested. However, this presents a problem when you want to use paths that have a separator in their name; the tokenizer cannot properly understand what you mean by '/a/b/c' if it is possible for '/' to exist as a valid character in a key name.

To get around this, you can sidestep the whole "filesystem path" style, and abandon the separator entirely, by using lists as paths. All of the methods in dpath.* support the use of a list instead of a string as a path. So for example:

.. code-block:: python

   >>> x = { 'a': {'b/c': 0}}
   >>> dpath.get(['a', 'b/c'])
   0

.. _re_regexp:

Globs too imprecise? Use Python's `re` Regular Expressions
==========================================================

Python's `re` regular expressions PythonRe_ may be used as follows:

  .. _PythonRe:  https://docs.python.org/3/library/re.html

  -  This facility must be enabled (for backwards compatibility):

   .. code-block:: python

     >>> import dpath
	 >>> dpath.options.DPATH_ACCEPT_RE_REGEXP = True

  -  Now a path component may also be specified : 

     - in a path expression, as {<re.regexpr>} where `<re.regexpr>` is a regular expression
       accepted by the  standard Python module `re`. For example:

      .. code-block:: python 

       >>> selPath = 'Config/{(Env|Cmd)}'
       >>> x = dpath.util.search(js.lod, selPath)

      .. code-block:: python

       >>> selPath = '{(Config|Graph)}/{(Env|Cmd|Data)}'
       >>> x = dpath.util.search(js.lod, selPath)

     - When using the list form for a path, a list element can also
       be expressed as
   
       -  a string as above
       -  the output of ::    `re.compile( args )``

       An example:

       .. code-block:: python

        >>> selPath = [ re.compile('(Config|Graph)') , re.compile('(Env|Cmd|Data)') ]
        >>>  x = dpath.util.search(js.lod, selPath)

       More examples from a realistic json context:

       +-----------------------------------------+--------------------------------------+
       +     **Extended path glob**              |  **Designates**                      + 
       +-----------------------------------------+--------------------------------------+
       +     "\*\*/{[^A-Za-z]{2}$}"              |   "Id"                               +
       +-----------------------------------------+--------------------------------------+
       +     r"\*/{[A-Z][A-Za-z\\d]*$}"          |  "Name","Id","Created", "Scope",...  +
       +-----------------------------------------+--------------------------------------+
       +     r"\*\*/{[A-Z][A-Za-z\\d]*\d$}"      |   EnableIPv6"                        +
       +-----------------------------------------+--------------------------------------+
       +     r"\*\*/{[A-Z][A-Za-z\\d]*Address$}" |   "Containers/199c5/MacAddress"      +
       +-----------------------------------------+--------------------------------------+
       
       With Python's chararcter string conventions, required backslashes in the `re` syntax
       can be entered either in raw strings or using double backslashes, thus
       the following are equivalent:

        +-----------------------------------------+----------------------------------------+
        +    *with raw strings*                   | *equivalent* with double backslash     +
        +-----------------------------------------+----------------------------------------+
        +    r"\*\*/{[A-Z][A-Za-z\\d]*\\d$}"      |   "\*\*/{[A-Z][A-Za-z\\\\d]*\\\\d$}"   +
        +-----------------------------------------+----------------------------------------+
        +   r"\*\*/{[A-Z][A-Za-z\\d]*Address$}"   |  "\*\*/{[A-Z][A-Za-z\\\\d]*Address$}"  +
        +-----------------------------------------+----------------------------------------+

.. _duck_string_match:

Need still more customization ? Roll your own match method!
===========================================================

We provide the following abstract types, where `StringMatcher` is allowed in Glob in the
sequence form (definitions in `dpath.types`) :

- `StringMatcher` (descriptive ),

- `Duck_StringMatcher`: which will accept a class as a **subtype**, provided it offers
    a `match` method. Instances may then be used as components in the list form of paths. 
    This method of structural subtyping is explained in PEP 544 [https://peps.python.org/pep-0544/].

- `Basic_StringMatcher` which can be used as a base class, enabling your derivec class to be 
   recognized and participate in a match.

**Note** The mechanisms used by Duck_StringMatcher are not available on all versions
of Python and Pypy, so you may need to revert to using Basic_StringMatcher. The
variable dpath.options.PEP544_PROTOCOL_AVAILABLE indicates when duck typing is possible.

Then it is up to you... Examples are provided in `tests/test_duck_typing.py`,
  including:

  - match anagrams and 

  - approximate match:

  .. code-block:: python 

      class Anagram():
           def __init__(self, s):
               self.ref = "".join(sorted(s))
    
           def match(self, st):
               retval = True if "".join(sorted(st)) == self.ref else None
               return retval

       mydict = TestBasics.mydict
    
       r1 = DP.search(mydict, "**/label")
       r2 = DP.search(mydict, [ '**', Anagram("bella")])

       assert r1 == r2



  .. code-block:: python

        class Approx():
            def __init__(self, s, quality=90):
                self.ref = s
                self.quality=quality

            def match(self, st):
                fratio = rapidfuzz.fuzz.ratio(st, self.ref)
                retval = True if fratio > self.quality  else None
                return retval

        mydict = TestBasics.mydict


        r1 = DP.search(mydict, "**/placeholder")
        r2 = DP.search(mydict, [ '**', Approx("placecolder")])
        r3 = DP.search(mydict, [ '**', Approx("acecolder",75)])
        assert r1 == r2
        assert r1 == r3

For comparison, the first example redone to avoid duck typing:

  .. code-block:: python

       if not DP.options.PEP544_PROTOCOL_AVAILABLE:
             class Anagram(DP.types.Basic_StringMatcher):
                def __init__(self, s):
                    self.ref = "".join(sorted(s))

                def match(self, st):
                    retval = True if "".join(sorted(st)) == self.ref else None
                    return retval

       DP.search(mydict, ['**', Anagram("bella")])

dpath.segments : The Low-Level Backend
======================================

dpath is where you want to spend your time: this library has the friendly
functions that will understand simple string globs, afilter functions, etc.

dpath.segments is the backend pathing library. It passes around tuples of path
components instead of string globs.

.. |PyPI| image:: https://img.shields.io/pypi/v/dpath.svg?style=flat
    :target: https://pypi.python.org/pypi/dpath/
    :alt: PyPI: Latest Version

.. |Python Version| image:: https://img.shields.io/pypi/pyversions/dpath?style=flat
    :target: https://pypi.python.org/pypi/dpath/
    :alt: Supported Python Version

.. |Build Status| image:: https://github.com/dpath-maintainers/dpath-python/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/dpath-maintainers/dpath-python/actions/workflows/tests.yml
   
.. |Gitter| image:: https://badges.gitter.im/dpath-python/chat.svg
    :target: https://gitter.im/dpath-python/chat?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge
    :alt: Gitter

Contributors
============

We would like to thank the community for their interest and involvement. You
have all made this project significantly better than the sum of its parts, and
your continued feedback makes it better every day. Thank you so much!

The following authors have contributed to this project, in varying capacities:

+ Caleb Case <calebcase@gmail.com>
+ Andrew Kesterson <andrew@aklabs.net>
+ Marc Abramowitz <marc@marc-abramowitz.com>
+ Richard Han <xhh2a@berkeley.edu>
+ Stanislav Ochotnicky <sochotnicky@redhat.com>
+ Misja Hoebe <misja@conversify.com>
+ Gagandeep Singh <gagandeep.2020@gmail.com>
+ Alan Gibson <alan.gibson@gmail.com>

And many others! If we've missed you please open an PR and add your name here.
