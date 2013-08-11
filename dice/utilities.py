from __future__ import absolute_import, unicode_literals

import pyparsing

def classname(obj):
    """Returns the name of an objects class"""
    return obj.__class__.__name__

def patch_pyparsing():
    """Applies monkey-patches to pyparsing"""
    disable_artity_trimming()

def disable_artity_trimming():
    """When pyparsing encounters a TypeError when calling a parse action, it
    will keep trying the call the function with one less argument each time
    until it succeeds. This disables this functionality, as it catches
    TypeErrors raised by other functions and makes debugging those functions
    very hard to do."""

    def _trim_arity(func, maxargs=None):
        def wrapper(string, location, tokens):
            return func(string, location, tokens)
        return wrapper

    pyparsing._trim_arity = _trim_arity
