from __future__ import absolute_import, unicode_literals, division

from dice.elements import Integer, Roll
from dice import roll


class TestInteger(object):
    def test_value(self):
        assert roll('1337') == 1337

    def test_type(self):
        assert isinstance(roll('1'), int)
        assert isinstance(roll('1'), Integer)


class TestDice(object):
    def test_dice_value(self):
        assert 0 < int(roll('d6')) <= 6
        assert 0 < int(roll('1d6')) <= 6

    def test_dice_type(self):
        assert isinstance(roll('d6'), Roll)
        assert isinstance(roll('1d6'), Roll)

    def test_dice_values(self):
        for die in roll('6d6'):
            assert 0 < die <= 6


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

    def test_total(self):
        assert (6 * 1) <= roll('6d6t') <= (6 * 6)

    def test_sort(self):
        value = roll('6d6s')
        assert value == sorted(value)
        assert isinstance(value, Roll)

    def test_drop(self):
        value = roll('6d6 v 3')
        assert len(value) == 3

    def test_keep(self):
        value = roll('6d6 ^ 3')
        assert len(value) == 3


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
