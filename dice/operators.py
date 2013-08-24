"""Operator elements"""

from __future__ import absolute_import, print_function, unicode_literals

import operator

from dice.elements import Element
from dice.utilities import classname

class Operator(Element):
    @classmethod
    def parse(cls, string, location, tokens):
        return cls(operands=tokens)

    def __init__(self, operands):
        self.operands = operands

    def __repr__(self):
        return "{0}({1})".format(
            classname(self),
            ', '.join(map(repr, self.operands)))

    def evaluate(self):
        raise NotImplementedError(
            "Operator subclass has no evaluate()")

    def evaluate_operands(self):
        self.operands = map(self.evaluate_object, self.operands)
        return self.operands


class FunctionOperator(Operator):
    @property
    def function(self):
        raise NotImplementedError(
            "FunctionOperator subclass has no function")

    def evaluate(self):
        return self.function(*self.evaluate_operands())


class Div(FunctionOperator):
    function = operator.floordiv


class Mul(FunctionOperator):
    function = operator.mul


class Sub(FunctionOperator):
    function = operator.sub


class Add(FunctionOperator):
    function = operator.add
