"""Tests for the dice package"""

from __future__ import absolute_import, print_function

def single(iterable):
    return iterable[0] if len(iterable) == 1 else list(iterable)

def parse(grammar, string):
    """Parses a string with a grammar, returning and printing the result"""
    return single(grammar.parseString(string, parseAll=True))
