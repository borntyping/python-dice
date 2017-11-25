from __future__ import absolute_import

import itertools
from dice import roll, roll_min, roll_max
from dice.command import main


def test_roll():
    for single, raw in itertools.product((True, False), (True, False)):
        assert roll('6d6', single=single, raw=raw)
        assert roll_min('6d6', single=single, raw=raw)
        assert roll_max('6d6', single=single, raw=raw)


def test_main(capsys):
    main(['2d6'])


def test_main_verbose():
    main(['2d6', '--verbose'])


def test_main_min(capsys):
    main(['2d6', '--min'])


def test_main_max():
    main(['2d6', '--max'])
