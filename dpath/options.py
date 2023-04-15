from os import environ

ALLOW_EMPTY_STRING_KEYS = False

DPATH_ACCEPT_RE_REGEXP_IN_STRING = False
"""Enables regular expression support.

Enabling this feature will allow usage of regular expressions as part of paths.
Regular expressions must be wrapped in curly brackets. For example: "a/b/{[cd]}".
Expressions will be compiled using the standard library re.compile function.
"""

# ----------------------------------------------------------------------------------------------
# undocumented feature for testability: facilitate running the entire package (or test suite)
# with option enabled/disabled by setting "DPATH_ACCEPT_RE_REGEXP_IN_STRING" in process environment.
#   Value => Effect
#   TRUE : set to True
#   TRUE_PRINT: set to True and output confirmation to stderr
#   FALSE: set to False
#   FALSE_PRINT: set to False and output confirmation to stderr
if "DPATH_ACCEPT_RE_REGEXP_IN_STRING" in environ:
    setTrue = environ["DPATH_ACCEPT_RE_REGEXP_IN_STRING"]
    if setTrue in ("TRUE", "TRUE_PRINT"):
        DPATH_ACCEPT_RE_REGEXP_IN_STRING = True
    else:
        DPATH_ACCEPT_RE_REGEXP_IN_STRING = False

    if setTrue[-5:] == "PRINT":
        from sys import stderr
        print(f"DPATH_ACCEPT_RE_REGEXP_IN_STRING={DPATH_ACCEPT_RE_REGEXP_IN_STRING}", file=stderr)
