"""Objects used in the evaluation of the parse tree"""

from __future__ import absolute_import, print_function, unicode_literals

import random
import operator

from dice.utilities import classname


class Element(object):
    verbose = False

    def evaluate(self):
        """Evaluate the current object - a no-op by default"""
        return self

    def evaluate_object(self, obj, cls=None):
        """Evaluates elements, and coerces objects to a class if needed"""
        if isinstance(obj, Element):
            obj = obj.evaluate_cached()
        if cls is not None:
            obj = cls(obj)
        return obj

    def evaluate_cached(self, verbose=None):
        """Wraps evaluate(), caching results"""
        if not hasattr(self, 'result'):
            self.result = self.evaluate()
            if self.verbose:
                print("Evaluating:", str(self), "->", str(self.result))
        return self.result


class Integer(int, Element):
    """A wrapper around the int class"""

    verbose = False

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
        return '[' + ', '.join(map(str, self)) + ']'

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

    def __repr__(self):
        return "Dice({0!r}, {1!r})".format(self.amount, self.sides)

    def __str__(self):
        return "{0!s}d{1!s}".format(self.amount, self.sides)

    def evaluate(self):
        self.amount = self.evaluate_object(self.amount, Integer)
        self.sides = self.evaluate_object(self.sides, Integer)
        return Roll(self.amount, self.sides)


class Operator(Element):
    @classmethod
    def parse(cls, string, location, tokens):
        return cls(*tokens)

    def __init__(self, *operands):
        self.operands = self.orginal_operands = operands

    def __repr__(self):
        return "{0}({1})".format(
            classname(self), ', '.join(map(str, self.orginal_operands)))

    def evaluate(self):
        self.operands = map(self.evaluate_object, self.operands)
        return self.function(*self.operands)

    @property
    def function(self):
        raise NotImplementedError("Operator subclass has no function")


class IntegerOperator(Operator):
    def evaluate_object(self, obj):
        return super(IntegerOperator, self).evaluate_object(obj, Integer)


class Div(IntegerOperator):
    function = operator.floordiv


class Mul(IntegerOperator):
    function = operator.mul


class Sub(IntegerOperator):
    function = operator.sub


class Add(IntegerOperator):
    function = operator.add


class Total(Operator):
    function = sum


class Sort(Operator):
    def function(self, iterable):
        iterable.sort()
        return iterable


class Drop(Operator):
    def function(self, iterable, n):
        for die in sorted(iterable)[:n]:
            iterable.remove(die)
        return iterable


class Keep(Operator):
    def function(self, iterable, n):
        for die in sorted(iterable)[:-n]:
            iterable.remove(die)
        return iterable
