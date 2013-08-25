"""A library for parsing and evaluating dice notation."""

from __future__ import absolute_import, print_function, unicode_literals

import argparse

import dice.grammar
import dice.utilities

__all__ = ['roll', 'main', 'ParseException']
__author__ = "Sam Clements <sam@borntyping.co.uk>"
__version__ = "0.2.1"

from pyparsing import ParseException

parser = argparse.ArgumentParser()
parser.add_argument(
    '-V', '--version', action='version',
    version='dice v{0} by {1}'.format(__version__, __author__))
parser.add_argument(
    '-v', '--verbose', action='store_true',
    help="show additional output")
parser.add_argument(
    'expression',
    help="the expression to parse and roll")

def parse(string, grammar):
    """Returns an AST parsed from an expression"""
    return grammar.parseString(string, parseAll=True)

def evaluate(string, grammar, **options):
    """Parse and then evaluate a string with a grammar"""
    return [e.evaluate(**options) for e in parse(string, grammar)]

def roll(string, verbose=False):
    """Parses and evaluates an expression"""
    return evaluate(string, grammar=dice.grammar.expression, verbose=verbose)

def main(argv=None):
    args = parser.parse_args(argv)
    result = roll(args.expression, verbose=args.verbose)
    result = dice.utilities.single(result)
    if args.verbose:
        print("Result:", end=" ")
    return result
