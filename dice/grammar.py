"""
Dice notation grammar

PyParsing is patched to make it easier to work with, by removing features
that get in the way of development and debugging. See the dice.utilities
module for more information.
"""

from __future__ import absolute_import, unicode_literals, division
from __future__ import print_function

from pyparsing import (CaselessLiteral, Forward, Group, Keyword, Literal,
    OneOrMore, Optional, ParserElement, StringStart, StringEnd, Suppress,
    Word, ZeroOrMore, delimitedList, nums, opAssoc, operatorPrecedence)

from dice.elements import Integer, Dice
from dice.utilities import patch_pyparsing

# Set PyParsing options
patch_pyparsing()
ParserElement.enablePackrat()
# ParserElement.verbose_stacktrace = True

# An integer value
integer = Word(nums).setParseAction(Integer.parse).setName("integer")

# An expression in dice notation
expression = operatorPrecedence(integer, [
    (Literal('d').suppress(), 2, opAssoc.LEFT, Dice.parse),
    (Literal('d'), 1, opAssoc.RIGHT, Dice.parse_default),

    (Literal('+'), 2, opAssoc.LEFT),
    (Literal('-'), 2, opAssoc.LEFT),
    (Literal('*'), 2, opAssoc.LEFT),
    (Literal('/'), 2, opAssoc.LEFT),
]).setName("expression")

# Multiple expressions can be separated with delimiters
notation = StringStart() + delimitedList(expression, ';') + StringEnd()
notation.setName("notation")
