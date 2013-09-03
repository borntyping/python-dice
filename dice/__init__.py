"""A library for parsing and evaluating dice notation."""

from __future__ import absolute_import, print_function, unicode_literals

from pyparsing import ParseException

import dice.elements
import dice.grammar
import dice.utilities

__all__ = ['roll', 'ParseException']
__author__ = "Sam Clements <sam@borntyping.co.uk>"
__version__ = '0.4.2'


def roll(string, single=True, verbose=False):
    """Parses and evaluates a dice expression"""
    ast = dice.grammar.expression.parseString(string, parseAll=True)
    result = [element.evaluate_cached(verbose=verbose) for element in ast]
    if single:
        return dice.utilities.single(result)
    return result
