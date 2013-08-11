from __future__ import absolute_import, unicode_literals

import warnings

import pyparsing

def classname(obj):
    """Returns the name of an objects class"""
    return obj.__class__.__name__

def patch_pyparsing(packrat=True, arity=True, verbose=True):
    """Applies monkey-patches to pyparsing"""
    if packrat:
        enable_pyparsing_packrat()

    if arity:
        disable_pyparsing_arity_trimming()

    if verbose:
        enable_pyparsing_verbose_stacktrace()

def enable_pyparsing_packrat():
    """Enables pyparsing's packrat parsing, which is much faster for the type
    of parsing being done in this library"""
    pyparsing.ParserElement.enablePackrat()

def enable_pyparsing_verbose_stacktrace():
    """Enables verbose stacktraces in pyparsing"""
    pyparsing.ParserElement.verbose_stacktrace = True

def _trim_arity(func, maxargs=None):
    def wrapper(string, location, tokens):
        return func(string, location, tokens)
    return wrapper

def disable_pyparsing_arity_trimming():
    """When pyparsing encounters a TypeError when calling a parse action, it
    will keep trying the call the function with one less argument each time
    until it succeeds. This disables this functionality, as it catches
    TypeErrors raised by other functions and makes debugging those functions
    very hard to do."""
    warnings.warn("Disabled pyparsing arity trimming", ImportWarning)
    pyparsing._trim_arity = _trim_arity
