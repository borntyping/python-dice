from __future__ import absolute_import

from pyparsing import ParseException, ParseFatalException
from py.test import raises

from dice.elements import (Integer, Roll, WildRoll, Dice, FudgeDice, Total,
                           MAX_ROLL_DICE, TooManyDice)
from dice import roll, roll_min, roll_max


class TestElements(object):
    def test_integer(self):
        assert isinstance(Integer(1), int)

    def test_dice_construct(self):
        d = Dice(2, 6)
        assert d.amount == 2 and d.amount == 2 and d.sides == d.max_value == 6

    def test_dice_from_iterable(self):
        d = Dice.from_iterable((2, 6))
        assert d.amount == 2 and d.sides == 6

    def test_dice_from_string(self):
        d = Dice.from_string('2d6')
        assert d.amount == 2 and d.sides == 6

    def test_roll(self):
        amount, sides = 6, 6
        assert len(Roll.roll(amount, 1, sides)) == amount
        rr = Roll.roll(amount, 1, sides)
        assert (1 * sides) <= sum(rr) <= (amount * sides)

    def test_list(self):
        assert roll('1, 2, 3') == [1, 2, 3]

    def test_special_rhs(self):
        assert roll('d%', raw=True).max_value == 100
        fudge = roll('dF', raw=True)
        assert fudge.min_value == -1 and fudge.max_value == 1

    def test_extreme_roll(self):
        assert roll_min('3d6') == [1] * 3
        assert roll_max('3d6') == [6] * 3

    def test_fudge(self):
        amount, _range = 6, 6
        fdice = FudgeDice(amount, _range)
        assert fdice.min_value == -_range and fdice.max_value == _range
        froll = fdice.evaluate()
        assert len(froll) == amount
        assert -(amount * _range) <= sum(froll) <= (amount * _range)

    def test_wild(self):
        amount, sides = 6, 6
        assert len(WildRoll.roll(amount, 1, sides)) >= amount
        rr = WildRoll.roll(amount, 1, sides)
        assert 0 <= sum(rr)


class TestErrors(object):
    exc_types = (ParseException, ParseFatalException)

    def test_toomanydice(self):
        with raises(TooManyDice):
            roll('%id6' % (MAX_ROLL_DICE + 1))


class TestEvaluate(object):
    def test_cache(self):
        """Test that evaluation returns the same result on successive runs"""
        roll('6d(6d6)t')
        ast = Total(Dice(6, Dice(6, 6)))
        assert ast.evaluate_cached() is ast.evaluate_cached()

    def test_multiargs(self):
        """Test that binary operators function properly when repeated"""
        assert roll('1d1+1d1+1d1') == 3
        assert roll('1d1-1d1-1d1') == -1
        assert roll('1d1*1d1*1d1') == 1
        assert roll('1d1/1d1/1d1') == 1
