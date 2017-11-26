from __future__ import absolute_import

from pyparsing import Literal, ParseFatalException
from py.test import raises
import random
import string

from dice import roll, utilities
from dice.utilities import verbose_print
from dice.elements import RandomElement, FudgeDice


def test_enable_pyparsing_packrat_parsing():
    """Test that packrat parsing was enabled"""
    import pyparsing
    assert pyparsing.ParserElement._packratEnabled is True


def test_disable_pyparsing_arity_trimming():
    """Test that pyparsing._trim_arity has been replaced"""
    import pyparsing
    import dice.utilities
    assert pyparsing._trim_arity is dice.utilities._trim_arity


def test_disable_pyparsing_arity_trimming_works():
    """Tests that arity trimming has been disabled and parse actions with
    the wrong number of arguments will raise TypeErrors"""
    for func in [lambda a: None, lambda a, b: None, lambda a, b, c, d: None]:
        element = Literal('test').setParseAction(func)
        with raises(TypeError):
            element.parseString('test')


class TestVerbosePrint(object):
    def _get_vprint(self, expr):
        raw = roll(expr, raw=True)
        evaluated = raw.evaluate_cached()
        vprint = verbose_print(raw)
        return evaluated, vprint

    def test_dice_simple(self):
        v = self._get_vprint('6d6')[1]
        assert v.startswith('roll 6d6 -> ')

    def test_dice_complex(self):
        v = self._get_vprint('6d(6d6)t')[1]
        lines = v.split('\n')
        stripped = [l.strip() for l in lines]

        assert len(lines) == 6
        assert lines[0] == 'Total('
        assert stripped[1] == 'Dice('
        assert stripped[2] == '6,'
        assert stripped[3].startswith('roll 6d6')
        assert stripped[4].startswith(') -> ')
        assert stripped[5].startswith(') -> ')

    def test_unevaluated(self):
        r = roll('d20', raw=True)
        v = verbose_print(r)
        assert v.startswith('roll 1d20 -> ')

    def test_single_line(self):
        v = self._get_vprint('d6x')[1]
        assert len(v.split('\n')) == 1


class TestDiceSwitch(object):
    def test_seperator_map(self):
        for sep, cls in RandomElement.DICE_MAP.items():
            d = utilities.dice_switch(6, 6, sep)
            assert type(d) is cls

    def test_percentile(self):
        for sep, cls in RandomElement.DICE_MAP.items():
            d = utilities.dice_switch(6, '%', sep)
            assert d.sides == 100

    def test_fudge(self):
        assert type(utilities.dice_switch(1, 'f', 'd')) == FudgeDice
        assert type(utilities.dice_switch(1, 'f', 'u')) == FudgeDice

        with raises(ValueError):
            utilities.dice_switch(1, 'f', 'w')

    def test_invalid(self):
        unused = set(string.ascii_lowercase) - set(RandomElement.DICE_MAP)

        bad_params = [
            (1, 0, 'd'),
            (1, 6, 'dd')
        ]

        if unused:
            unused_char = random.choice(list(unused))
            bad_params.append((1, 6, unused_char))

        for params in bad_params:
            with raises(ValueError):
                utilities.dice_switch(*params)


def test_binary_stack():
    with raises(ParseFatalException):
        roll('6d6d6')


def test_too_many_explosions():
    with raises(ParseFatalException):
        while True:
            roll('1000d1000x2')
