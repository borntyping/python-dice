"""A library for parsing and evaluating dice notation."""

from __future__ import absolute_import, print_function, unicode_literals

import sys
import argparse

import dice.grammar
import dice.utilities

__all__ = ['roll', 'main', 'Dice', 'Roll', 'Bag', 'ParseException']
__author__ = "Sam Clements <sam@borntyping.co.uk>"
__version__ = "0.2.0"

from pyparsing import ParseException
from dice.elements import Dice, Roll, Bag

parser = argparse.ArgumentParser()
parser.add_argument(
    '-v', '--version', action='version',
    version='dice v{0} by {1}'.format(__version__, __author__))
parser.add_argument(
    '-s', '--single', action='store_true', dest='single',
    help="if a single element is returned, extract it from the list")
parser.add_argument(
    'expression',
    help="the expression to parse and roll")

def roll(string, single=False):
    result = dice.grammar.notation.parseString(string, parseAll=True)
    return dice.utilities.single(result) if single else result

def main(*argv):
    args = parser.parse_args(sys.argv if len(argv) == 0 else argv)

    return roll(args.expression, single=args.single)
