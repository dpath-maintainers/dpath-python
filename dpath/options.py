from os import environ

ALLOW_EMPTY_STRING_KEYS = False

#  Extension to interpret path segments "{rrr}" as re.regexp "rrr" disabled by default.
#  Disable to preserve backwards compatibility in the case where a user has a
#  path "a/b/{cd}" where the brackets are intentional and do not denote a request
#  to re.compile cd
#  Enable to allow segment matching with Python re regular expressions.

DPATH_ACCEPT_RE_REGEXP_IN_STRING = False

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
