from dice import roll, roll_min, roll_max
from dice.command import main
from itertools import product
from pytest import raises


def test_roll():
    for single, raw in product((True, False), (True, False)):
        assert roll("6d6", single=single, raw=raw)
        assert roll_min("6d6", single=single, raw=raw)
        assert roll_max("6d6", single=single, raw=raw)


def test_main():
    main(["2d6"])


def test_main_verbose():
    main(["2d6", "--verbose"])


def test_main_min():
    main(["2d6", "--min"])


def test_main_max():
    main(["2d6", "--max"])


def test_main_max_dice():
    main(["2d6", "--max-dice", "2"])


def test_main_max_dice_err():
    with raises(SystemExit):
        main(["2d6", "--max-dice", "not_a_number"])


def test_main_error():
    with raises(SystemExit):
        main(["d0"])


def test_main_error2():
    """Test placing the error on the left"""
    with raises(SystemExit):
        main(["000000000000000000000000000000000000000001d6, d0"])
