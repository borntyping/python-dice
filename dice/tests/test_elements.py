from __future__ import absolute_import

from dice.elements import Integer, Roll, Dice, Total
from dice import roll


class TestElements(object):
    def test_integer(self):
        assert isinstance(Integer(1), int)

    def test_dice_from_iterable(self):
        d = Dice.from_iterable((2, 6))
        assert d.amount == 2 and d.sides == 6

    def test_dice_from_string(self):
        d = Dice.from_string('2d6')
        assert d.amount == 2 and d.sides == 6

    def test_roll(self):
        amount, sides = 6, 6
        assert len(Roll.roll(amount, sides)) == amount
        assert (1 * sides) <= sum(Roll.roll(amount, sides)) <= (amount * sides)


class TestEvaluate(object):
    def test_cache(self):
        """Test that evaluation returns the same result on successive runs"""
        roll('6d(6d6)t')
        ast = Total(Dice(6, Dice(6, 6)))
        assert ast.evaluate_cached() is ast.evaluate_cached()
