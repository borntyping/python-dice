"""Objects used in the evaluation of the parse tree"""

from __future__ import absolute_import, unicode_literals, division

import random
import copy

import six

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
        return [random.randint(1, sides) for i in range(amount)]

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
    def parse_binary(cls, string, location, tokens):
        return cls(*tokens)

    @classmethod
    def parse_unary(cls, string, location, tokens):
        return cls(1, *tokens)

    @classmethod
    def from_iterable(cls, iterable):
        return cls(*iterable)

    @classmethod
    def from_string(cls, string):
        amount, sides = string.split('d', 1)
        return cls(int(amount), int(sides))

    def __init__(self, amount, sides):
        self.amount, self.sides = int(amount), int(sides)

    def __repr__(self):
        return "Dice('{0}d{1}')".format(self.amount, self.sides)

    def __str__(self):
        return "{0}d{1}".format(self.amount, self.sides)

    def __int__(self):
        # TODO: Remove this when dice are evaluated
        return int(self.roll())

    def roll(self, cls=Roll):
        return cls(self)

class Bag(list):
    """A collection of dice objects"""

    @staticmethod
    def dice_from_object(obj, cls=Dice):
        if isinstance(obj, cls):
            return copy.copy(obj)
        elif isinstance(obj, six.string_types):
            return cls.from_string(obj)
        elif isinstance(obj, (tuple, list)):
            return cls.from_iterable(obj)
        raise TypeError("Dice object cannot be created from " + repr(obj))

    def __init__(self, *dice_list):
        for d in dice_list:
            self.append(self.dice_from_object(d))

    def __repr__(self):
        return "Bag({0})".format(','.join(map(repr, self)))

    def __str__(self):
        return ', '.join(map(str, self))

    def roll(self):
        return [d.roll() for d in self]
