"""A library for parsing and evaluating dice notation."""

from __future__ import absolute_import, print_function, unicode_literals

import argparse

import dice.grammar
import dice.utilities

__all__ = ['parse', 'roll', 'main', 'ParseException']
__author__ = "Sam Clements <sam@borntyping.co.uk>"
__version__ = "0.2.0"

from pyparsing import ParseException

parser = argparse.ArgumentParser()
parser.add_argument(
    '-v', '--version', action='version',
    version='dice v{0} by {1}'.format(__version__, __author__))
parser.add_argument(
    'expression',
    help="the expression to parse and roll")

def _(obj):
    print(obj)
    return obj

def parse(string, grammar):
    """Returns an AST parsed from an expression"""
    return _(grammar.parseString(string, parseAll=True))

def evaluate(string, grammar):
    """Parse and then evaluate a string with a grammar"""
    return _([element.evaluate() for element in parse(string, grammar)])

def roll(string):
    """Parses and evaluates an expression"""
    return evaluate(string, dice.grammar.expression)

def main(argv=None):
    args = parser.parse_args(argv)
    result = roll(args.expression)
    print("Result:", dice.utilities.single(result))
    return result
