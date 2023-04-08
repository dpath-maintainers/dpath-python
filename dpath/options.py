ALLOW_EMPTY_STRING_KEYS = False

#  Extension to interpret path segments "{rrr}" as re.regexp "rrr" enabled by default.
#  Disable to preserve backwards compatibility in the case where a user has a
#  path "a/b/{cd}" where the brackets are intentional and do not denote a request
#  to re.compile cd
DPATH_ACCEPT_RE_REGEXP = True
