"""Objects used in the evaluation of the parse tree"""

from __future__ import absolute_import, print_function, unicode_literals

import random
import operator
from pyparsing import ParseFatalException

from dice.utilities import (classname, addevensubodd, do_explode, do_reroll,
                            dice_switch)

EXTREME_MIN = object()
EXTREME_MAX = object()
MAX_ROLL_DICE = 2**20
DICE_MAP = {}


def register_dice(cls):
    if not issubclass(cls, RandomElement):
        raise TypeError('can only register RandomElement subclasses as dice')
    elif not cls.SEPERATOR:
        raise TypeError('must specify seperator')
    elif cls.SEPERATOR in DICE_MAP:
        raise RuntimeError('seperator %s already registered' % cls.SEPERATOR)
    DICE_MAP[cls.SEPERATOR] = cls
    return cls


class TooManyDice(ParseFatalException):
    pass


class Element(object):
    def evaluate(self, **kwargs):
        """Evaluate the current object - a no-op by default"""
        return self

    @staticmethod
    def evaluate_object(obj, cls=None, cache=False, **kwargs):
        """Evaluates elements, and coerces objects to a class if needed"""
        if isinstance(obj, Element):
            if cache:
                obj = obj.evaluate_cached(**kwargs)
            else:
                obj = obj.evaluate(cache=cache, **kwargs)

        if cls is not None:
            obj = cls(obj)

        return obj

    def evaluate_cached(self, **kwargs):
        """Wraps evaluate(), caching results"""
        if not hasattr(self, 'result'):
            self.result = self.evaluate(cache=True, **kwargs)

        return self.result


class Integer(int, Element):
    """A wrapper around the int class"""

    @classmethod
    def parse(cls, string, location, tokens):
        return cls(tokens[0])


class IntegerList(list, Element):
    "Augments the standard list with an __int__ operator"
    def __str__(self):
        ret = '[%s]' % ', '.join(map(str, self))
        if hasattr(self, "sum") and len(self) > 1:
            ret += ' -> %i' % self
        return ret

    def __int__(self):
        ret = sum(self)
        self.sum = ret
        return ret


class Roll(IntegerList):
    "Represents a randomized result from a random element"

    @classmethod
    def roll_single(cls, min_value, max_value, **kwargs):
        min_value = cls.evaluate_object(min_value, Integer, **kwargs)
        max_value = cls.evaluate_object(max_value, Integer, **kwargs)

        if min_value > max_value:
            raise ParseFatalException('Roll must have a valid range')

        return random.randint(min_value, max_value)

    @classmethod
    def roll(cls, amount, min_value, max_value, **kwargs):
        amount = cls.evaluate_object(amount, Integer, **kwargs)

        if amount > MAX_ROLL_DICE:
            raise TooManyDice("The number of dice is too damn high!")
        elif amount < 0:
            raise ParseFatalException("Cannot roll less than zero dice!")

        return [cls.roll_single(min_value, max_value, **kwargs)
                for i in range(amount)]

    def do_roll_single(self, min_value=None, max_value=None, **kwargs):
        element = self.random_element

        if self.force_extreme is EXTREME_MIN:
            return element.min_value
        elif self.force_extreme is EXTREME_MAX:
            return element.max_value

        if min_value is None:
            min_value = element.min_value

        if max_value is None:
            max_value = element.max_value

        return self.roll_single(min_value, max_value, **kwargs)

    def do_roll(self, amount=None, min_value=None, max_value=None, **kwargs):
        element = self.random_element
        if amount is None:
            amount = element.amount
        if min_value is None:
            min_value = element.min_value
        if max_value is None:
            max_value = element.max_value

        return self.roll(amount, min_value, max_value, **kwargs)

    def __init__(self, element, rolled=None, **kwargs):
        self.random_element = element
        self.force_extreme = kwargs.get('force_extreme')

        amount = self.evaluate_object(element.amount, Integer, **kwargs)
        min_value = self.evaluate_object(element.min_value, Integer, **kwargs)
        max_value = self.evaluate_object(element.max_value, Integer, **kwargs)

        if rolled is None:
            if self.force_extreme is EXTREME_MIN:
                rolled = [min_value] * amount
            elif self.force_extreme is EXTREME_MAX:
                rolled = [max_value] * amount
            else:
                rolled = self.do_roll(**kwargs)

        super(Roll, self).__init__(rolled)

    def __repr__(self):
        return "{0}({1}, random_element={2!r})".format(
            classname(self), str(self), self.random_element)


class WildRoll(Roll):
    "Represents a roll of wild dice"

    @classmethod
    def roll(cls, amount, min_value, max_value, **kwargs):
        amount = cls.evaluate_object(amount, Integer, **kwargs)
        min_value = cls.evaluate_object(min_value, Integer, **kwargs)
        max_value = cls.evaluate_object(max_value, Integer, **kwargs)

        if amount == 0:
            return []

        rolls = [random.randint(min_value, max_value) for i in range(amount)]

        if min_value == max_value:
            return rolls  # Continue as if dice were normal instead of erroring

        while rolls[-1] == max_value:
            rolls.append(random.randint(min_value, max_value))

        if len(rolls) == amount and rolls[-1] == min_value:  # failure
            rolls[-1] = 0
            rolls[rolls.index(max(rolls))] = 0
            if random.randint(min_value, max_value) == min_value:
                return [0] * amount

        return rolls


class ExplodedRoll(Roll):
    "Represents an exploded roll"
    def __init__(self, original, rolled, **kwargs):
        super(ExplodedRoll, self).__init__(original, rolled=rolled, **kwargs)


class RandomElement(Element):
    "Represents a set of elements with a random numerical result"

    SEPERATOR = None

    @classmethod
    def parse(cls, string, location, tokens):
        return cls(*tokens)

    @classmethod
    def parse_unary(cls, string, location, tokens):
        return cls(1, *tokens)

    @classmethod
    def from_iterable(cls, iterable):
        return cls(*iterable)

    @classmethod
    def from_string(cls, string):
        string = string.lower()
        for k in DICE_MAP:
            ss = string.split(k)
            if len(ss) != 2:
                continue
            ss = [int(x) if x.isdigit() else x for x in ss]
            return dice_switch(ss[0], ss[1], k)

    def __init__(self, amount, min_value, max_value, **kwargs):
        self.amount = amount
        self.min_value = min_value
        self.max_value = max_value

    def evaluate(self, **kwargs):
        return Roll(self, **kwargs)


@register_dice
class Dice(RandomElement):
    """A group of dice, all with the same number of sides"""

    SEPERATOR = 'd'

    def __init__(self, amount, max_value, min_value=1):
        super(Dice, self).__init__(amount, min_value, max_value)
        self.sides = max_value
        self.original_operands = (amount, max_value)

    def __repr__(self):
        return "{0}({1!r}, {2!r})".format(type(self).__name__,
                                          self.amount, self.max_value)

    def __str__(self):
        return "{0!s}{1}{2!s}".format(self.amount, self.SEPERATOR, self.sides)


@register_dice
class WildDice(Dice):
    "A group of dice with the last being explodable or a failure mode on 1"

    SEPERATOR = 'w'

    def evaluate(self, **kwargs):
        return WildRoll(self, **kwargs)


@register_dice
class FudgeDice(Dice):
    "A group of dice whose sides range from -x to x, including 0"

    SEPERATOR = 'u'

    def __init__(self, amount, range):
        super(FudgeDice, self).__init__(amount, range, -range)


class Operator(Element):
    @classmethod
    def parse(cls, string, location, tokens):
        return cls(*tokens)

    def __init__(self, *operands):
        self.operands = self.original_operands = operands

    def __repr__(self):
        return "{0}({1})".format(
            classname(self), ', '.join(map(str, self.original_operands)))

    def preprocess_operands(self, *operands, **kwargs):
        def eval_wrapper(operand):
            return self.evaluate_object(operand, **kwargs)

        return [eval_wrapper(o) for o in operands]

    def evaluate(self, **kwargs):
        if not kwargs.get('cache', False):
            self.operands = self.original_operands

        self.operands = self.preprocess_operands(*self.operands, **kwargs)

        try:
            return self.function(*self.operands)
        except TypeError:
            value = self.operands[0]
            for o in self.operands[1:]:
                value = self.function(value, o)
            return value

    @property
    def function(self):
        raise NotImplementedError("Operator subclass has no function")


class IntegerOperator(Operator):
    def preprocess_operands(self, *operands, **kwargs):
        def eval_wrapper(operand):
            return self.evaluate_object(operand, Integer, **kwargs)

        return [eval_wrapper(o) for o in operands]


class RHSIntegerOperator(Operator):
    def preprocess_operands(self, *operands, **kwargs):
        ret = [self.evaluate_object(operands[0], **kwargs)]
        for operand in operands[1:]:
            ret.append(self.evaluate_object(operand, Integer, **kwargs))
        return ret


class Div(IntegerOperator):
    function = operator.floordiv


class Mul(IntegerOperator):
    function = operator.mul


class Sub(IntegerOperator):
    function = operator.sub


class Add(IntegerOperator):
    function = operator.add


class AddEvenSubOdd(Operator):
    function = addevensubodd


class Total(Operator):
    function = sum


class Successes(RHSIntegerOperator):
    def function(self, iterable, thresh):
        if not isinstance(iterable, IntegerList):
            iterable = (iterable,)
        elif isinstance(iterable, Roll):
            if thresh > iterable.random_element.max_value:
                raise ParseFatalException("Success threshold higher than "
                                          " roll result.")
        return sum(x >= thresh for x in iterable)


class SuccessFail(Operator):
    def function(self, iterable, thresh):
        result = 0
        if not isinstance(iterable, IntegerList):
            iterable = (iterable,)
        elif isinstance(iterable, Roll):
            if thresh > iterable.random_element.max_value:
                raise ParseFatalException("Success threshold higher than "
                                          "maximum roll result.")

        if isinstance(iterable, Roll):
            fail_level = iterable.random_element.min_value
        else:
            fail_level = 1

        for x in iterable:
            if x >= thresh:
                result += 1
            elif x <= fail_level:
                result -= 1

        return result


class Sort(Operator):
    def function(self, iterable):
        if not isinstance(iterable, IntegerList):
            iterable = list(iterable)
        iterable.sort()
        return iterable


class Extend(Operator):
    def function(self, *args):
        ret = IntegerList()
        for x in args:
            try:
                ret.extend(x)
            except TypeError:
                ret.append(x)
        return ret


class Array(Operator):
    def function(self, *args):
        ret = IntegerList()
        for x in args:
            try:
                x = sum(x)
            except TypeError:
                pass
            ret.append(x)
        return ret


class Lowest(RHSIntegerOperator):
    def function(self, iterable, n=None):
        if not isinstance(iterable, IntegerList):
            raise ParseFatalException("Can't take the lowest values of "
                                      "a scalar!")
        if n is None:
            n = len(iterable) - 1
        iterable = sorted(iterable)[:n]
        random.shuffle(iterable)
        return IntegerList(iterable)


class Highest(RHSIntegerOperator):
    def function(self, iterable, n=None):
        if not isinstance(iterable, IntegerList):
            raise ParseFatalException("Can't take the highest values of "
                                      "a scalar!")
        if n is None:
            n = len(iterable) - 1
        iterable = sorted(iterable)[-n:]
        random.shuffle(iterable)
        return IntegerList(iterable)


class Middle(RHSIntegerOperator):
    def function(self, iterable, n=None):
        if not isinstance(iterable, IntegerList):
            raise ParseFatalException("Can't take the middle values of "
                                      "a scalar!")
        num = len(iterable)
        if n is None:
            n = (num - 2) if num > 2 else 1

        num_remove = num - n
        upper = num_remove // 2
        lower = num_remove - upper

        iterable = sorted(iterable)[lower:-upper]
        random.shuffle(iterable)  # nobody has to know :v
        return IntegerList(iterable)


class Explode(RHSIntegerOperator):
    def function(self, roll, thresh=None):
        if not isinstance(roll, Roll):
            raise ParseFatalException('Cannot explode {0}'.format(roll))
        elif thresh is None:
            thresh = roll.random_element.max_value

        if thresh == roll.random_element.min_value:
            raise ParseFatalException('Refusing to explode with threshold '
                                      'same as min roll.')
        return do_explode(roll, thresh)


class Reroll(RHSIntegerOperator):
    def function(self, roll, thresh=None):
        if not isinstance(roll, Roll):
            raise ParseFatalException('Cannot reroll {0}'.format(roll))
        return do_reroll(roll, thresh)


class ForceReroll(RHSIntegerOperator):
    def function(self, roll, thresh=None):
        if not isinstance(roll, Roll):
            raise ParseFatalException('Cannot reroll {0}'.format(roll))
        return do_reroll(roll, thresh, force_min=True)


class Identity(Operator):
    # no function defined because of passthrough __new__
    def __new__(self, x):
        return x


class Negate(Operator):
    def function(self, operand):
        try:
            operand = list(operand)
            for i, x in enumerate(operand):
                operand[i] = -x
            return operand
        except TypeError:
            return -operand


class ArrayAdd(RHSIntegerOperator):
    def function(self, iterable, scalar):
        try:
            scalar = int(scalar)
            iterable = list(iterable)
            for i, x in enumerate(iterable):
                iterable[i] = x + scalar
            return iterable
        except TypeError:
            raise ParseFatalException('Invalid operands for array add')


class ArraySub(RHSIntegerOperator):
    def function(self, iterable, scalar):
        try:
            scalar = int(scalar)
            iterable = list(iterable)
            for i, x in enumerate(iterable):
                iterable[i] = x - scalar
            return iterable
        except TypeError:
            raise ParseFatalException('Invalid operands for array sub')
