"""A library for parsing and evaluating dice notation."""

from __future__ import absolute_import, print_function, unicode_literals

from pyparsing import ParseException
from dice.elements import TooManyDice

import dice.elements
import dice.grammar
import dice.utilities

__all__ = ['roll', 'roll_min', 'roll_max', 'ParseException', 'TooManyDice',
           'elements', 'grammar', 'command', 'utilities']
__author__ = ("Sam Clements <sam@borntyping.co.uk>, "
              "Caleb Johnson <me@calebj.io>")
__version__ = '2.1.0'


def roll(string, **kwargs):
    """Parses and evaluates a dice expression"""
    return _roll(string, **kwargs)


def roll_min(string, **kwargs):
    """Parses and evaluates the minimum of a dice expression"""
    return _roll(string, force_extreme=dice.elements.EXTREME_MIN, **kwargs)


def roll_max(string, **kwargs):
    """Parses and evaluates the maximum of a dice expression"""
    return _roll(string, force_extreme=dice.elements.EXTREME_MAX, **kwargs)


def parse_expression(string):
    return dice.grammar.expression.parseString(string, parseAll=True)


def _roll(string, single=True, raw=False, return_kwargs=False, **kwargs):
    ast = parse_expression(string)
    elements = list(ast)

    if not raw:
        elements = [element.evaluate_cached(**kwargs) for element in elements]

    if single:
        elements = dice.utilities.single(elements)

    if return_kwargs:
        return elements, kwargs

    return elements
