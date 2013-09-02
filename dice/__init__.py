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


def roll(string, single=True, verbose=False):
    """Parses and evaluates an expression"""
    ast = dice.grammar.expression.parseString(string, parseAll=True)
    result = [element.evaluate(verbose=verbose) for element in ast]
    if single:
        return dice.utilities.single(result)
    return result


def main(argv=None):
    args = parser.parse_args(argv)
    result = roll(args.expression, verbose=args.verbose)
    if args.verbose:
        print("Result:", end=" ")
    return result
