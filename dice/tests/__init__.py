"""Tests for the dice package"""

from __future__ import absolute_import, print_function

from py.test import raises

def single(iterable):
    return iterable[0] if len(iterable) == 1 else list(iterable)

def parse(grammar, string):
    """Parses a string with a grammar, returning and printing the result"""
    result = single(grammar.parseString(string))
    print(result)
    return result
