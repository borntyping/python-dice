from __future__ import absolute_import, unicode_literals, division

from dice.elements import Integer, Dice
from dice.grammar import integer, expression, notation
from dice.tests import parse

class TestInteger(object):
    def test_parse(self):
        assert parse(integer, "1337") == 1337
        assert parse(notation, "1337") == 1337

    def test_type(self):
        assert isinstance(parse(integer, "1"), int)
        assert isinstance(parse(integer, "1"), Integer)


class TestDice(object):
    def test_dice_type(self):
        for dice in ("d6", "1d6"):
            assert isinstance(parse(expression, dice), Dice)

    def test_dice_value(self):
        # TODO: This should not have to call roll()
        for dice in ("d6", "1d6"):
            assert 0 < int(parse(expression, dice).roll()) <= 6

    def test_dice_result(self):
        # TODO: This should not have to call roll()
        for result in parse(expression, "6d6").roll():
            assert 0 < result <= 6


class TestExpression(object):
    def test_expression(self):
        assert parse(notation, "2d6")

    def test_sub_expression(self):
        assert parse(notation, "(2d6)d(2d6)")

    def test_multiple_expressions(self):
        assert len(parse(notation, "6d6; 6d6")) == 2

    def test_multiple_expressions_types(self):
        for value in parse(notation, "6d6; 6d6"):
            assert isinstance(value, Dice)


class TestExpressionMaths(object):
    def test_add(self):
        assert parse(notation, "2 + 2") == 4

    def test_sub(self):
        assert parse(notation, "2 - 2") == 0

    def test_mul(self):
        assert parse(notation, "2 * 2") == 4

    def test_div(self):
        assert parse(notation, "2 / 2") == 1

    def test_operator_precedence_1(self):
        assert parse(notation, "16 / 8 * 4 + 2 - 1") == 9

    def test_operator_precedence_2(self):
        assert parse(notation, "16 - 8 + 4 * 2 / 1") == 16

    def test_operator_precedence_3(self):
        assert parse(notation, "10 - 3 + 2") == 9

    def test_operator_precedence_4(self):
        assert parse(notation, "1 + 2 * 3") == 7
