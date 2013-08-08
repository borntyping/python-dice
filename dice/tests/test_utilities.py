from __future__ import absolute_import

from pyparsing import Literal

from dice.tests import raises

def test_disable_arity_trimming():
    """Tests that arity trimming has been disabled and parse actions with
    the wrong number of arguments will raise TypeErrors"""
    for func in [lambda a: None, lambda a, b: None, lambda a, b, c, d: None]:
        element = Literal("test").setParseAction(func)
        with raises(TypeError):
            element.parseString("test")
