from os import environ

ALLOW_EMPTY_STRING_KEYS = False

ALLOW_REGEX = "DPATH_ALLOW_REGEX" in environ
"""Enables regular expression support.

Enabling this feature will allow usage of regular expressions as part of paths.
Regular expressions must be wrapped in curly brackets. For example: "a/b/{[cd]}".
Expressions will be compiled using the standard library re.compile function.
"""
