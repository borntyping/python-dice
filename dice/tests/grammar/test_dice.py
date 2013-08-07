from __future__ import absolute_import, unicode_literals, division

from dice.grammar import Dice, dice, expression
from dice.tests import parse

def roll(string):
    return dice.parseString(string)

def test_dice_type():
    assert isinstance(parse(dice, "1d6"), Dice)

def test_dice_result():
    for result in parse(dice, "6d6").evaluate():
        assert 0 < result <= 6

def test_expression_len():
    assert len(parse(expression, "6d6; 6d6")) == 2

def test_expression_types():
    for value in parse(expression, "6d6; 6d6"):
        assert isinstance(value, Dice)
