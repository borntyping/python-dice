from __future__ import absolute_import

import itertools

from dice import roll
from dice.command import main


def test_roll():
    for single, verbose in itertools.product((True, False), (True, False)):
        assert roll('6d6', single=single, verbose=verbose)


def test_main():
    assert isinstance(main(['2d6']), str)


def test_main_verbose():
    assert main(['1d6', '--verbose'])
