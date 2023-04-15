ALLOW_EMPTY_STRING_KEYS = False

#  Extension to interpret path segments "{rrr}" as re.regexp "rrr" disabled by default.
#  Disable to preserve backwards compatibility in the case where a user has a
#  path "a/b/{cd}" where the brackets are intentional and do not denote a request
#  to re.compile cd
#  Enable to allow segment matching with Python re regular expressions.
DPATH_ACCEPT_RE_REGEXP_IN_STRING = False
