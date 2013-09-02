from __future__ import absolute_import

from dice.command import main
from dice.elements import Integer, Roll


def test_main():
    assert isinstance(main(['2d6']), (Integer, Roll, list))

def test_main_verbose():
    assert main(['1d6', '--verbose'])
