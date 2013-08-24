from __future__ import absolute_import, unicode_literals, division

from dice.elements import Integer, Roll
from dice.grammar import integer, expression
from dice.tests import parse

class TestInteger(object):
    def test_parse(self):
        assert parse(integer, "1337") == 1337
        assert parse(expression, "1337") == 1337

    def test_type(self):
        assert isinstance(parse(integer, "1"), int)
        assert isinstance(parse(integer, "1"), Integer)


class TestDice(object):
    def test_dice_type(self):
        for dice in ("d6", "1d6"):
            assert isinstance(parse(expression, dice), Roll)

    def test_dice_value(self):
        for dice in ("d6", "1d6"):
            assert 0 < int(parse(expression, dice)) <= 6

    def test_dice_result(self):
        for result in parse(expression, "6d6"):
            assert 0 < result <= 6


class TestExpression(object):
    def test_expression(self):
        assert parse(expression, "2d6")

    def test_sub_expression(self):
        assert parse(expression, "(2d6)d(2d6)")


class TestExpressionMaths(object):
    def test_add(self):
        assert parse(expression, "2 + 2") == 4

    def test_sub(self):
        assert parse(expression, "2 - 2") == 0

    def test_mul(self):
        assert parse(expression, "2 * 2") == 4

    def test_div(self):
        assert parse(expression, "2 / 2") == 1

    def test_operator_precedence_1(self):
        assert parse(expression, "16 / 8 * 4 + 2 - 1") == 9

    def test_operator_precedence_2(self):
        assert parse(expression, "16 - 8 + 4 * 2 / 1") == 16

    def test_operator_precedence_3(self):
        assert parse(expression, "10 - 3 + 2") == 9

    def test_operator_precedence_4(self):
        assert parse(expression, "1 + 2 * 3") == 7
