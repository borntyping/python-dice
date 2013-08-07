from __future__ import absolute_import, unicode_literals, division

from dice import ParseException
from dice.grammar import subexpr, expression
from dice.tests import parse, raises

def test_subexpr():
    assert parse(expression, "(2d6)")

def test_subexpr_fail():
    with raises(ParseException):
        parse(subexpr, "(2d6")
