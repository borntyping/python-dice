from __future__ import absolute_import, unicode_literals, division

from dice.grammar import integer, expression
from dice.tests import parse

def test_integer():
    assert parse(integer, "1337") == 1337

def test_integer_type():
    assert isinstance(parse(integer, "1"), int)
