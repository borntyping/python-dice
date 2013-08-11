"""Objects used in the evaluation of the parse tree"""

from __future__ import absolute_import, unicode_literals, division
from __future__ import print_function

from collections import Iterable
from random import randint

from six import string_types
from pyparsing import ParseResults

from dice.utilities import classname

class Roll(list):
    """A result from rolling a group of dice"""

    def __init__(self, dice):
        super(Roll, self).__init__(self.roll(dice.num, dice.sides))
        self.sides = dice.sides

    def __repr__(self):
        return "{0}({1}, sides={0})".format(
            classname(self), str(self), self.sides)

    def __str__(self):
        return ', '.join(self)

    @staticmethod
    def roll(num, sides):
        return [randint(1, sides) for i in range(num)]

class Dice(object):
    """A group of dice, all with the same number of sides"""

    @classmethod
    def parse(cls, string, location, tokens):
        assert len(tokens) == 2
        return cls(tokens[0:2])

    def __init__(self, obj):
        if isinstance(obj, string_types):
            self.assign(*obj.split('d'))
        elif isinstance(obj, Iterable):
            self.assign(*obj)
        else:
            raise TypeError("Cannot create Dice object from {0}".format(
                obj.__class__.__name__))

    def assign(self, num, sides):
        self.num, self.sides = int(num), int(sides)

    def __repr__(self):
        return "Dice('{0}d{1}')".format(self.num, self.sides)

    def __str__(self):
        return "{0}d{1}".format(self.num, self.sides)

    def evaluate(self, cls=Roll):
        return cls(self)

class Integer(int):
    """A wrapper around the int class"""

    @classmethod
    def parse(cls, string, location, tokens):
        assert len(tokens) == 1
        return cls(tokens[0])
