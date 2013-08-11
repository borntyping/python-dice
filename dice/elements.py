"""Objects used in the evaluation of the parse tree"""

from __future__ import absolute_import, unicode_literals, division
from __future__ import print_function

from collections import Iterable
from random import randint

from six import string_types
from pyparsing import ParseResults

from dice.utilities import classname

class Integer(int):
    """A wrapper around the int class"""

    @classmethod
    def parse(cls, string, location, tokens):
        return cls(tokens[0])

class Roll(list):
    """A result from rolling a group of dice"""

    @staticmethod
    def roll(amount, sides):
        return [randint(1, sides) for i in range(amount)]

    def __init__(self, dice):
        super(Roll, self).__init__(self.roll(dice.amount, dice.sides))
        self.sides = dice.sides

    def __repr__(self):
        return "{0}({1}, sides={0})".format(
            classname(self), str(self), self.sides)

    def __str__(self):
        return ', '.join(self)

    def __int__(self):
        return sum(self)

class Dice(object):
    """A group of dice, all with the same number of sides"""

    @classmethod
    def parse(cls, string, location, tokens):
        return cls(tokens[0][0], tokens[0][1])

    @classmethod
    def parse_default(cls, string, location, tokens):
        return cls(1, tokens[0][1])

    @classmethod
    def from_string(cls, string):
        return cls(*[int(x) for x in string.split('d')])

    def __init__(self, amount, sides):
        self.amount, self.sides = int(amount), int(sides)

    def __repr__(self):
        return "Dice('{0}d{1}')".format(self.amount, self.sides)

    def __str__(self):
        return "{0}d{1}".format(self.amount, self.sides)

    def __int__(self):
        # TODO: Remove this when dice are evaluated
        return int(self.evaluate())

    def evaluate(self, cls=Roll):
        return cls(self)
