from __future__ import absolute_import

from pyparsing import Literal

from py.test import raises


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
