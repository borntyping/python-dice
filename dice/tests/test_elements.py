from __future__ import absolute_import

import re

import py.test

from dice.elements import Integer, Roll, Dice, Bag

@py.test.fixture
def dice_constructors():
    return Dice(2, 6), "2d6", (2, 6)

@py.test.fixture
def bag():
    return Bag("1d2", "2d4", "4d6", "6d8", "8d10")

def test_integer():
    assert isinstance(Integer(1), int)

def test_roll():
    assert isinstance(Dice(2, 6).roll(), Roll)

def test_dice_from_iterable():
    d = Dice.from_iterable((2, 6))
    assert d.amount == 2 and d.sides == 6

def test_dice_from_string():
    d = Dice.from_string("2d6")
    assert d.amount == 2 and d.sides == 6

def test_dice_from_object(dice_constructors):
    for obj in dice_constructors:
        d = Bag.dice_from_object(obj)
        assert d.amount == 2 and d.sides == 6

def test_dice_from_object_exception():
    with py.test.raises(TypeError):
        Bag.dice_from_object(NotImplemented)

def test_bag_length(dice_constructors):
    assert len(Bag(*dice_constructors)) == len(dice_constructors)

def test_bag_str(bag):
    assert re.match("[d,\d]*", str(bag))
