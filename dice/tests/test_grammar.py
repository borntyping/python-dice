from __future__ import absolute_import, unicode_literals, division

from pyparsing import Word, opAssoc
from dice.elements import Integer, Roll, WildRoll, ExplodedRoll
from dice.exceptions import DiceException, DiceFatalException
from dice import roll, roll_min, roll_max, grammar
from py.test import raises


class TestInteger(object):
    def test_value(self):
        assert roll('1337') == 1337

    def test_type(self):
        assert isinstance(roll('1'), int)
        assert isinstance(roll('1'), Integer)


class TestDice(object):
    def test_dice_value(self):
        assert 0 < int(roll('d6')) <= 6
        assert 0 < int(roll('6d6')) <= 36

        assert 0 < int(roll('d%')) <= 100
        assert 0 < int(roll('6d%')) <= 600

        assert -1 <= int(roll('dF')) <= 1
        assert -6 <= int(roll('6dF')) <= 6
        assert -6 <= int(roll('u6')) <= 6
        assert -36 < int(roll('6u6')) <= 36

        assert 0 <= int(roll('w6'))
        assert 0 <= int(roll('6w6'))

        assert 0 < int(roll('d6x'))
        assert 0 < int(roll('6d6x'))

    def test_dice_type(self):
        assert isinstance(roll('d6'), Roll)
        assert isinstance(roll('6d6'), Roll)
        assert isinstance(roll('d%'), Roll)
        assert isinstance(roll('6d%'), Roll)

        assert isinstance(roll('dF'), Roll)
        assert isinstance(roll('6dF'), Roll)
        assert isinstance(roll('u6'), Roll)
        assert isinstance(roll('6u6'), Roll)

        assert isinstance(roll('w6'), WildRoll)
        assert isinstance(roll('6w6'), WildRoll)

        assert isinstance(roll('d6x'), ExplodedRoll)
        assert isinstance(roll('6d6x'), ExplodedRoll)

    def test_dice_values(self):
        for die in roll('6d6'):
            assert 0 < die <= 6

    def test_nested_dice(self):
        assert 1 <= roll('d(d6)t') <= 6
        assert -6 <= roll('u(d6)t') <= 6


class TestOperators(object):
    def test_add(self):
        assert roll('2 + 2') == 4

    def test_sub(self):
        assert roll('2 - 2') == 0

    def test_mul(self):
        assert roll('2 * 2') == 4
        assert roll('1d6 * 2') % 2 == 0

    def test_div(self):
        assert roll('2 / 2') == 1

    def test_mod(self):
        assert roll('5 % 3') == 2
        assert roll('1 % 3') == 1
        assert 0 <= roll('d6 % 3') <= 2

    def test_identity(self):
        assert roll('+2') == 2
        assert roll('+(1, 2)') == [1, 2]

    def test_negate(self):
        assert roll('-2') == -2
        assert roll('-(1, 2)') == [-1, -2]

    def test_aeso(self):
        assert roll('+-1') == -1
        assert roll('+-2') == 2
        assert roll('+-(1, 2)') == [-1, 2]


class TestVectorOperators(object):
    def test_total(self):
        assert (6 * 1) <= roll('6d6t') <= (6 * 6)

    def test_sort(self):
        value = roll('6d6s')
        assert value == sorted(value)
        assert isinstance(value, Roll)

        with raises(DiceFatalException):
            roll('6s')

    def test_drop(self):
        value = roll('6d6 v 3')
        assert len(value) == 3

        value = roll('(1, 2, 5, 9, 3) v 3')
        assert set(value) == set([1, 2, 3])

        value = roll('6d6v')
        assert len(value) == 5

        value = roll('6d6v(-3)')
        assert len(value) == 3

        with raises(DiceFatalException):
            roll('6 v 3')

    def test_keep(self):
        value = roll('6d6 ^ 3')
        assert len(value) == 3

        value = roll('(1, 2, 5, 9, 3) ^ 3')
        assert set(value) == set([3, 5, 9])

        value = roll('6d6^')
        assert len(value) == 5

        value = roll('6d6^(-3)')
        assert len(value) == 3

        with raises(DiceFatalException):
            roll('6 ^ 3')

    def test_middle(self):
        value = roll('6d6 o 3')
        assert len(value) == 3

        value = roll('(1, 2, 5, 9, 3) o 3')
        assert set(value) == set([2, 3, 5])

        value = roll('6d6o')
        assert len(value) == 4

        with raises(DiceFatalException):
            roll('6 o 3')

        assert len(roll('6d6o(-4)')) == 2

    def test_successes(self):
        assert roll('(2, 4, 6, 8) e 5') == 2
        assert roll('6 e 5') == 1
        assert roll('100d20e1') == 100
        with raises(DiceFatalException):
            roll('d20 e 21')
        with raises(DiceFatalException):
            roll('d(d6) e 6')

    def test_successe_failures(self):
        assert roll('(1, 2, 4, 6, 8) f 5') == 1
        assert roll('6 f 5') == 1
        assert roll('100d20f1') == 100
        with raises(DiceFatalException):
            roll('d20 f 21')
        with raises(DiceFatalException):
            roll('d(d6) f 6')

    def test_array_add(self):
        assert roll('(2, 4, 6, 8) .+ 2') == [4, 6, 8, 10]

    def test_array_sub(self):
        assert roll('(2, 4, 6, 8) .- 2') == [0, 2, 4, 6]

    def test_array(self):
        rr = roll('2d6, 3d6, 4d6')
        assert len(rr) == 3

    def test_extend(self):
        rr = roll('2d6 | 3d6, 4d6')
        assert len(rr) == 4

        rr2 = roll('2d6 | 3d6 | 4d6')
        assert len(rr2) == 9

        rr3 = roll('2d6 | 3d6 | 10 | 4d6')
        assert len(rr3) == 10


class TestDiceOperators(object):
    def test_reroll(self):
        r = roll('6d6r')
        assert len(r) == 6

    def test_force_reroll(self):
        r2 = roll('1000d6rr')
        assert 1 not in r2

        r3 = roll('100d6rr5')
        assert all(x > 5 for x in r3)

    def test_extreme_reroll(self):
        r = roll_min('2d6r')
        assert r == [1, 1]

        r = roll_max('2d6r6')
        assert r == [6, 6]

    def test_again_roll(self):
        while True:
            r = roll('6d6a')
            if 6 in r:
                break

        num_6 = r.count(6)
        assert 6 == len(r) - (num_6 // 2)

    def test_again_scalar(self):
        assert roll('6a6') == [6, 6]

    def test_again_vector(self):
        assert roll('(1,2,3)a2') == [1, 2, 2, 3]
        assert roll("(1|1|1)a1") == [1, 1, 1, 1, 1, 1]


class TestErrors(object):
    exc_types = (DiceException, DiceFatalException)

    def run_test(self, expr, exceptions=exc_types):
        with raises(exceptions, message='Expectiong %s to fail!' % expr):
            roll(expr)

    def test_bad_operators(self):
        for expr in ('6d', '1+', '[1,2,3]', 'f', '3f', '3x', '6.+6', '7.-7'):
            self.run_test(expr)

    def test_invalid_rolls(self):
        for expr in ('(0-1)d6', '6d(0-1)',
                     'd0', '6d0'):
            self.run_test(expr)

    def test_unmatched_parenthesis(self):
        for expr in ('(6d6', '6d6)'):
            self.run_test(expr)

    def test_explode_min(self):
        self.run_test('6d6x1')
        self.run_test('6d6x(1-2)')

    def test_explode_onesided(self):
        self.run_test('6d1x')

    def test_invalid_reroll(self):
        for expr in ('6r', '(1,2)r', '6rr', '(1,2)rr',
                     'd(d6)rr', 'u(d6)r'):
            self.run_test(expr)

    def test_div_zero(self):
        self.run_test('1/0')
        self.run_test('1/(0*1)')

    def test_again_fail(self):
        self.run_test('(1,2,3)a')
        self.run_test('1a')


class TestOperatorPrecedence(object):
    def test_operator_precedence_1(self):
        assert roll('16 / 8 * 4 + 2 - 1') == 9

    def test_operator_precedence_2(self):
        assert roll('16 - 8 + 4 * 2 / 1') == 16

    def test_operator_precedence_3(self):
        assert roll('10 - 3 + 2') == 9

    def test_operator_precedence_4(self):
        assert roll('1 + 2 * 3') == 7


class TestExpression(object):
    def test_expression(self):
        assert isinstance(roll('2d6'), Roll)

    def test_sub_expression(self):
        assert isinstance(roll('(2d6)d(2d6)'), Roll)


class TestBadPrecedence(object):
    def test_invalid_arity(self):
        with raises(Exception):
            grammar.operatorPrecedence(
                grammar.integer,
                [(Word('0'), 3, opAssoc.LEFT, Integer.parse)]
            )

    def test_invalid_association(self):
        with raises(Exception):
            grammar.operatorPrecedence(
                grammar.integer,
                [(Word('0'), 2, None, Integer.parse)]
            )
