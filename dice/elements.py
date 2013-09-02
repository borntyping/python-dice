"""Objects used in the evaluation of the parse tree"""

from __future__ import absolute_import, print_function, unicode_literals

import random
import operator

from dice.utilities import classname


class Element(object):
    def evaluate(self, verbose=False):
        """Evaluate the current object - a no-op by default"""
        return self

    def evaluate_object(self, obj, cls=None):
        """Evaluates Elements, and optionally coerces objects to a class"""
        if isinstance(obj, Element):
            obj = obj.evaluate()
        if cls is not None:
            obj = cls(obj)
        return obj

    def print_evaluation(self, result):
        """Prints an explanation of an evaluation"""
        print("Evaluating:", str(self), "->", str(result))


class Integer(int, Element):
    """A wrapper around the int class"""

    @classmethod
    def parse(cls, string, location, tokens):
        return cls(tokens[0])


class Roll(list, Element):
    """A result from rolling a group of dice"""

    @staticmethod
    def roll(amount, sides):
        return [random.randint(1, sides) for i in range(amount)]

    def __init__(self, amount, sides):
        super(Roll, self).__init__(self.roll(amount, sides))
        self.sides = sides

    def __repr__(self):
        return "{0}({1}, sides={2})".format(
            classname(self), str(self), self.sides)

    def __str__(self):
        return ', '.join(map(str, self))

    def __int__(self):
        return sum(self)


class Dice(Element):
    """A group of dice, all with the same number of sides"""

    @classmethod
    def parse_binary(cls, string, location, tokens):
        return cls(*tokens)

    @classmethod
    def parse_unary(cls, string, location, tokens):
        return cls(1, *tokens)

    @classmethod
    def from_iterable(cls, iterable):
        return cls(*iterable)

    @classmethod
    def from_string(cls, string):
        amount, sides = string.split('d', 1)
        return cls(int(amount), int(sides))

    def __init__(self, amount, sides):
        self.amount = amount
        self.sides = sides
        self.result = None

    def __repr__(self):
        return "Dice({0!r}, {1!r})".format(self.amount, self.sides)

    def __str__(self):
        return "{0!s}d{1!s}".format(self.amount, self.sides)

    def evaluate(self, verbose=False):
        self.amount = self.evaluate_object(self.amount, Integer)
        self.sides = self.evaluate_object(self.sides, Integer)

        if self.result is None:
            self.result = Roll(self.amount, self.sides)

        if verbose:
            self.print_evaluation(self.result)

        return self.result

    def roll(self):
        return self.evaluate(verbose=False)


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

    def evaluate(self, verbose=False):
        return self.function(*self.evaluate_operands())


class Div(FunctionOperator):
    function = operator.floordiv


class Mul(FunctionOperator):
    function = operator.mul


class Sub(FunctionOperator):
    function = operator.sub


class Add(FunctionOperator):
    function = operator.add


class Total(FunctionOperator):
    function = sum
