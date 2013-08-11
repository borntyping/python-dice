"""Dice notation grammar"""

from __future__ import absolute_import, unicode_literals, division

from pyparsing import (CaselessLiteral, Forward, Group, Literal, OneOrMore,
    Optional, ParserElement, StringStart, StringEnd, Suppress,
    Word, ZeroOrMore, delimitedList, nums)

from dice.elements import Dice, Integer

# Set PyParsing options
ParserElement.enablePackrat()
ParserElement.verbose_stacktrace = True

# Some definitions need to be available before they have been defined
expr, subexpr = Forward(), Forward()

# An integer value
integer = Word(nums)
integer.setParseAction(Integer.parse)
integer.setName("integer")

# A single set of dice, each with the number of sides and rolled as a group
dice = Optional(integer, default=1) + Suppress(CaselessLiteral('d')) + integer
dice.setParseAction(Dice.parse)
dice.setName("dice")

# Sub-expressions are surrounded by parenthesis
lparen, rparen = Suppress(Literal('(')), Suppress(Literal(')'))

# Sub-expressions allow atoms to be another expression surrounded by brackets
subexpr <<= lparen + expr + rparen
subexpr.setName("sub-expression")

# The smallest possible component of an expression
atom = dice | integer | subexpr
atom.setName("atom")

# An expression in dice notation
expr <<= atom
expr.setName("partial expression")

# Multiple expressions can be separated with delimiters
delimiter = Suppress(Literal(';'))
delimiter.setName("delimiter")

expressions = expr + ZeroOrMore(delimiter + expr)
expressions.setName("expressions")

expression = StringStart() + Group(expressions) + StringEnd()
expression.setName("expression")
expression.validate()
