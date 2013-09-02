from __future__ import absolute_import

from dice import roll, main
from dice.elements import Integer, Roll


def test_roll():
    assert isinstance(roll('2d6'), (Integer, Roll, list))


def test_main():
    assert isinstance(main(['2d6']), (Integer, Roll, list))
