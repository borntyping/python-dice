"""A library for parsing and evaluating dice notation."""

from __future__ import absolute_import, print_function, unicode_literals

from pyparsing import ParseBaseException

import dice.elements
import dice.grammar
import dice.utilities
from dice.constants import DiceExtreme
from dice.exceptions import (DiceBaseException, DiceException,
                             DiceFatalException)

__all__ = ['roll', 'roll_min', 'roll_max', 'elements', 'grammar', 'utilities',
           'command', 'DiceBaseException', 'DiceException',
           'DiceFatalException', 'DiceExtreme']
__author__ = ("Sam Clements <sam@borntyping.co.uk>, "
              "Caleb Johnson <me@calebj.io>")
__version__ = '2.3.5'


def roll(string, **kwargs):
    """Parses and evaluates a dice expression"""
    return _roll(string, **kwargs)


def roll_min(string, **kwargs):
    """Parses and evaluates the minimum of a dice expression"""
    return _roll(string, force_extreme=DiceExtreme.EXTREME_MIN, **kwargs)


def roll_max(string, **kwargs):
    """Parses and evaluates the maximum of a dice expression"""
    return _roll(string, force_extreme=DiceExtreme.EXTREME_MAX, **kwargs)


def parse_expression(string):
    return dice.grammar.expression.parseString(string, parseAll=True)


def _roll(string, single=True, raw=False, return_kwargs=False, **kwargs):
    try:
        ast = parse_expression(string)
        elements = list(ast)

        if not raw:
            elements = [element.evaluate_cached(**kwargs)
                        for element in elements]

        if single:
            elements = dice.utilities.single(elements)

        if return_kwargs:
            return elements, kwargs

        return elements
    except ParseBaseException as e:
        raise DiceBaseException.from_other(e)
