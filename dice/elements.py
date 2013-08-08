"""Objects used in the evaluation of the parse tree"""

from __future__ import absolute_import, unicode_literals, division
from __future__ import print_function

from random import randint

from pyparsing import ParseResults

class Roll(list):
    """A result from rolling a group of dice"""
    
    def __init__(self, dice):
        super(Roll, self).__init__(self.roll(dice))

    @staticmethod
    def roll(dice):
        return [randint(1, dice.sides) for i in range(dice.num)]

class Dice(object):
    """A group of dice, all with the same number of sides"""
    
    def __init__(self, obj):
        if isinstance(obj, basestring):
            self.assign(*obj.split('d'))
        elif isinstance(obj, ParseResults):
            self.assign(*obj[0:2])
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
