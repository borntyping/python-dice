from __future__ import absolute_import, unicode_literals, division

from py.test import mark

from dice import ParseException
from dice.elements import Integer, Dice
from dice.grammar import integer, expression, notation
from dice.tests import parse, raises

def test_expression():
    assert parse(notation, "2d6")

def test_sub_expression():
    assert parse(notation, "(2d6)d6")

def test_integer():
    assert parse(integer, "1337") == 1337

def test_integer_type():
    assert isinstance(parse(integer, "1"), int)
    assert isinstance(parse(integer, "1"), Integer)

def test_dice_type():
    assert isinstance(parse(expression, "1d6"), Dice)

def test_dice_result():
    for result in parse(expression, "6d6").evaluate():
        assert 0 < result <= 6

@mark.xfail
def test_notation():
    assert parse(expression, "2 * 2 / 2 * 2") == 1

def test_multiple_expressions():
    assert len(parse(notation, "6d6; 6d6")) == 2

def test_multiple_expressions_types():
    for value in parse(notation, "6d6; 6d6"):
        assert isinstance(value, Dice)
