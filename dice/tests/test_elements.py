from __future__ import absolute_import

from dice.constants import DiceExtreme
from dice.exceptions import DiceException, DiceFatalException
import pickle
from pytest import raises
import random

from dice.elements import (
    Integer,
    Roll,
    WildRoll,
    Dice,
    FudgeDice,
    Total,
    MAX_ROLL_DICE,
    Element,
    RandomElement,
    WildDice,
)
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
        d = Dice.from_string("2d6")
        assert type(d) is Dice
        assert d.amount == 2 and d.sides == 6

        w = Dice.from_string("2w6")
        assert type(w) is WildDice
        assert w.amount == 2 and w.sides == 6

        u = Dice.from_string("2u6")
        assert type(u) is FudgeDice
        assert u.amount == 2 and u.sides == 6

    def test_dice_format(self):
        amount, sides = 6, 6
        for sep, cls in RandomElement.DICE_MAP.items():
            d = cls(amount, sides)
            assert str(d) == "%i%s%i" % (amount, cls.SEPARATOR, sides)
            assert repr(d) == "%s(%i, %i)" % (cls.__name__, amount, sides)

    def test_roll(self):
        amount, sides = 6, 6
        assert len(Roll.roll(amount, 1, sides)) == amount

        rr = Roll.roll(amount, 1, sides)
        assert (1 * sides) <= sum(rr) <= (amount * sides)

        rr = roll("%id%i" % (amount, sides))
        r_min, r_max = rr.random_element.min_value, rr.random_element.max_value
        assert r_min <= rr.do_roll_single() <= r_max

    def test_list(self):
        assert roll("1, 2, 3") == [1, 2, 3]

    def test_special_rhs(self):
        assert roll("d%", raw=True).max_value == 100
        fudge = roll("dF", raw=True)
        assert fudge.min_value == -1 and fudge.max_value == 1

    def test_extreme_roll(self):
        assert roll_min("3d6") == [1] * 3
        assert roll_max("3d6") == [6] * 3

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

        assert WildRoll.roll(0, 1, sides) == []

        assert WildRoll.roll(1, 1, 1) == [1]

    def test_wild_success(self):
        while True:
            if len(WildRoll.roll(1, 1, 2)) > 1:
                break

    def test_wild_fail(self):
        while True:
            if WildRoll.roll(1, 1, 2) == [0]:
                break

    def test_wild_critfail(self):
        while True:
            if WildRoll.roll(3, 1, 2) == [0, 0, 0]:
                break


class TestErrors(object):
    def test_toomanydice(self):
        with raises(DiceFatalException):
            roll("%id6" % (MAX_ROLL_DICE + 1))

        with raises(DiceFatalException):
            roll("7d6", max_dice=6)

        with raises(ValueError):
            Roll.roll(6, 1, 6, max_dice=4)

    def test_negative_amount_extreme(self):
        with raises(ValueError):
            Roll.roll(-1, 1, 6, force_extreme=DiceExtreme.EXTREME_MAX)

    def test_roll_error(self):
        with raises(ValueError):
            Roll.roll(-1, 1, 6)

        with raises(ValueError):
            Roll.roll_single(4, 3)

        with raises(DiceFatalException):
            rolled = roll("6d6")
            rolled.do_roll_single(4, 3)

    def test_invalid_wrap(self):
        with raises(NotImplementedError):
            try:
                raise RuntimeError('blah')
            except Exception as e:
                raise DiceException.from_other(e)


class TestEvaluate(object):
    def test_cache(self):
        """Test that evaluation returns the same result on successive runs"""
        roll("6d(6d6)t")
        ast = Total(Dice(6, Dice(6, 6)))
        evals = [ast.evaluate_cached() for i in range(100)]
        assert len(set(evals)) == 1
        assert ast.evaluate_cached() is ast.evaluate_cached()

    def test_nocache(self):
        """Test that evaluation returns different result on successive runs"""
        ast = Total(Dice(6, Dice(6, 6)))
        evals = [ast.evaluate() for i in range(100)]
        assert len(set(evals)) > 1

    def test_multiargs(self):
        """Test that binary operators function properly when repeated"""
        assert roll("1d1+1d1+1d1") == 3
        assert roll("1d1-1d1-1d1") == -1
        assert roll("1d1*1d1*1d1") == 1
        assert roll("1d1/1d1/1d1") == 1


class TestRegisterDice(object):
    def test_reregister(self):
        class FooDice(RandomElement):
            SEPARATOR = "d"

        with raises(RuntimeError):
            RandomElement.register_dice(FooDice)

    def test_no_separator(self):
        class BarDice(RandomElement):
            pass

        with raises(TypeError):
            RandomElement.register_dice(BarDice)

    def test_not_random_element(self):
        class BazDice(Element):
            pass

        with raises(TypeError):
            RandomElement.register_dice(BazDice)


class TestSystemRandom(object):
    sysrandom = random.SystemRandom()

    # lowest, middle and highest operators use shuffle()
    def test_sysrandom_op(self):
        roll("6d6h1", random=self.sysrandom)

    def test_sysrandom_roll(self):
        roll("6d6", random=self.sysrandom)


class TestPickle(object):
    for expr in [
        '-d20',
        '4d6t',
        '+-(1,2,3)',
        '2d20h',
        '4d6h3s',
        '4dF - 2',
        '4*d%'
    ]:
        value = roll(expr, raw=True, single=False)
        pickled = pickle.dumps(value)
        clone = pickle.loads(pickled)
