from __future__ import absolute_import

from dice.elements import Integer, Roll, Dice


def test_integer():
    assert isinstance(Integer(1), int)


def test_dice_from_iterable():
    d = Dice.from_iterable((2, 6))
    assert d.amount == 2 and d.sides == 6


def test_dice_from_string():
    d = Dice.from_string('2d6')
    assert d.amount == 2 and d.sides == 6


def test_dice_roll():
    assert isinstance(Dice(2, 6).roll(), Roll)


def test_roll():
    amount, sides = 6, 6
    assert len(Roll.roll(amount, sides)) == amount
    assert (1 * sides) <= sum(Roll.roll(amount, sides)) <= (amount * sides)
