from __future__ import absolute_import

from dice import roll, roll_min, roll_max
from dice.command import main
import itertools
from py.test import raises


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


def test_main_max_dice():
    main(['2d6', '--max-dice', '2'])


def test_main_max_dice_err():
    with raises(SystemExit):
        main(['2d6', '--max-dice', 'not_a_number'])


def test_main_error():
    try:
        main(['d0'])
    except SystemExit:
        pass


def test_main_error2():
    "Test placing the error on the left"
    try:
        main(['000000000000000000000000000000000000000001d6, d0'])
    except SystemExit:
        pass
