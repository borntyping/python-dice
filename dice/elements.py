"""Objects used in the evaluation of the parse tree"""

from __future__ import absolute_import, print_function, unicode_literals

import random
import operator
from pyparsing import ParseFatalException
from copy import copy

from dice.constants import MAX_EXPLOSIONS, MAX_ROLL_DICE, DiceExtreme
from dice.exceptions import DiceFatalException
from dice.utilities import classname, addevensubodd, dice_switch


class Element(object):
    @classmethod
    def parse(cls, string, location, tokens):
        try:
            return cls(*tokens).set_parse_attributes(string, location, tokens)
        # The following only matters on python2 platforms, so is marked nocover
        except ArithmeticError as e:                               # nocover
            exc = DiceFatalException(string, location, e.args[0])  # nocover
            exc.__cause__ = None                                   # nocover
            raise exc                                              # nocover

    def set_parse_attributes(self, string, location, tokens):
        "Fluent API for setting parsed location"
        self.string = string
        self.location = location
        self.tokens = tokens
        return self

    def fatal(self, description, location=None, offset=0,
              cls=DiceFatalException):
        if location is None:
            location = self.location
        return cls(self.string, location + offset, description)

    def evaluate(self, **kwargs):
        """Evaluate the current object - a no-op by default"""
        return self

    @staticmethod
    def evaluate_object(obj, cls=None, cache=False, **kwargs):
        """Evaluates elements, and coerces objects to a class if needed"""
        old_obj = obj
        if isinstance(obj, Element):
            if cache:
                obj = obj.evaluate_cached(**kwargs)
            else:
                obj = obj.evaluate(cache=cache, **kwargs)

        if cls is not None and type(obj) != cls:
            obj = cls(obj)

        for attr in ('string', 'location', 'tokens'):
            if hasattr(old_obj, attr):
                setattr(obj, attr, getattr(old_obj, attr))

        return obj

    def evaluate_cached(self, **kwargs):
        """Wraps evaluate(), caching results"""
        if not hasattr(self, 'result'):
            self.result = self.evaluate(cache=True, **kwargs)

        return self.result


class Integer(int, Element):
    """A wrapper around the int class"""
    pass


class String(str, Element):
    """A wrapper around the str class"""
    pass


class IntegerList(list, Element):
    "Augments the standard list with an __int__ operator"
    def __str__(self):
        ret = '[%s]' % ', '.join(map(str, self))
        if hasattr(self, "sum") and len(self) > 1:
            ret += ' -> %i' % self
        return ret

    def copy(self):
        return type(self)(self)

    def clear(self):
        self[:] = []

    def __int__(self):
        ret = sum(self)
        self.sum = ret
        return ret


class Roll(IntegerList):
    "Represents a randomized result from a random element"

    @classmethod
    def roll_single(cls, min_value, max_value, **kwargs):
        integer_min = cls.evaluate_object(min_value, Integer, **kwargs)
        integer_max = cls.evaluate_object(max_value, Integer, **kwargs)

        if integer_min > integer_max:
            raise ValueError('Roll must have a valid range (got %s - %s, '
                             'which evaluated to %i - %i). Are you trying to '
                             'use a fudge roll as the sides?'
                             % (min_value, max_value, integer_min, integer_max
                                )
                             )

        return random.randint(integer_min, integer_max)

    @classmethod
    def roll(cls, orig_amount, min_value, max_value, **kwargs):
        amount = cls.evaluate_object(orig_amount, Integer, **kwargs)

        max_dice = kwargs.get('max_dice', MAX_ROLL_DICE)

        if amount > max_dice:
            raise ValueError("Too many dice! (max is %i)" % max_dice)
        elif amount < 0:
            raise ValueError("Cannot roll less than zero dice!")

        return [cls.roll_single(min_value, max_value, **kwargs)
                for i in range(amount)]

    def do_roll_single(self, min_value=None, max_value=None, **kwargs):
        element = self.random_element

        if self.force_extreme is DiceExtreme.EXTREME_MIN:
            return element.min_value
        elif self.force_extreme is DiceExtreme.EXTREME_MAX:
            return element.max_value

        if min_value is None:
            min_value = element.min_value

        if max_value is None:
            max_value = element.max_value
        try:
            return self.roll_single(min_value, max_value, **kwargs)
        except ValueError as e:
            exc = self.random_element.fatal(e.args[0])
            raise exc

    def do_roll(self, amount=None, min_value=None, max_value=None, **kwargs):
        element = self.random_element
        if amount is None:
            amount = element.amount
        if min_value is None:
            min_value = element.min_value
        if max_value is None:
            max_value = element.max_value

        try:
            return self.roll(amount, min_value, max_value, **kwargs)
        except ValueError as e:
            exc = self.random_element.fatal(e.args[0])
            exc.__cause__ = None
            raise exc

    def __init__(self, element, rolled=None, **kwargs):
        self.random_element = element
        self.force_extreme = kwargs.get('force_extreme')

        amount = self.evaluate_object(element.amount, Integer, **kwargs)
        min_value = self.evaluate_object(element.min_value, Integer, **kwargs)
        max_value = self.evaluate_object(element.max_value, Integer, **kwargs)

        if rolled is None:
            max_dice = kwargs.get('max_dice', MAX_ROLL_DICE)

            if amount > max_dice:
                msg = "Too many dice! (max is %i)" % max_dice
                exc = self.random_element.fatal(msg)
                exc.__cause__ = None
                raise exc
            elif amount < 0:
                msg = "Cannot roll less than zero dice!"

                if not isinstance(element.amount, int):
                    msg += ' (%s evaluated to %s)' % (element.amount, amount)

                exc = self.random_element.fatal(msg)
                exc.__cause__ = None
                raise exc

            elif self.force_extreme is DiceExtreme.EXTREME_MIN:
                rolled = [min_value] * amount
            elif self.force_extreme is DiceExtreme.EXTREME_MAX:
                rolled = [max_value] * amount
            else:
                rolled = self.do_roll(**kwargs)

        super(Roll, self).__init__(rolled)

    def copy(self):
        return type(self)(self.random_element, rolled=self,
                          force_extreme=self.force_extreme)

    # unused
    # def substitute(self, newcontents):
    #     return type(self)(self.random_element, rolled=newcontents,
    #                       force_extreme=self.force_extreme)

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

    DICE_MAP = {}
    SEPERATOR = None

    @classmethod
    def register_dice(cls, new_cls):
        if not issubclass(new_cls, RandomElement):
            raise TypeError('can only register subclasses of RandomElement')
        elif not new_cls.SEPERATOR:
            raise TypeError('must specify seperator')
        elif new_cls.SEPERATOR in cls.DICE_MAP:
            raise RuntimeError('seperator %s already registered'
                               % new_cls.SEPERATOR)
        cls.DICE_MAP[new_cls.SEPERATOR] = new_cls
        return new_cls

    @classmethod
    def parse_unary(cls, string, location, tokens):
        return cls.parse(string, location, [1] + list(tokens))

    @classmethod
    def parse(cls, string, location, tokens):
        if len(tokens) > 3:
            msg = ('Cannot stack dice operators! Try disabiguating your '
                   'expression with parentheses,')
            raise ParseFatalException(string, tokens[3].location, msg)

        amount, kind, dicetype = tokens
        try:
            ret = dice_switch(amount, dicetype, kind)
            return ret.set_parse_attributes(string, location, tokens)
        except ValueError as e:
            if len(e.args) > 1:
                if type(e.args[1]) is int:
                    location = tokens[e.args[1]].location
                # unused as of yet
                # elif isinstance(e.args[1], Element):
                #     location = e.args[1].location
            raise ParseFatalException(string, location, e.args[0])

    @classmethod
    def from_iterable(cls, iterable):
        return cls(*iterable)

    @classmethod
    def from_string(cls, string):
        string = string.lower()
        for k in cls.DICE_MAP:
            ss = string.split(k)
            if len(ss) != 2:
                continue
            ss = [int(x) if x.isdigit() else x for x in ss]
            return dice_switch(ss[0], ss[1], k)

    def __init__(self, amount, min_value, max_value, **kwargs):
        self.amount = amount
        self.min_value = min_value
        self.max_value = max_value

    def __neg__(self):
        new = copy(self)
        new.min_value, new.max_value = -new.max_value, -new.min_value
        return new

    def __eq__(self, other):
        return type(self) is type(other) and \
               self.amoun == other.amount and \
               self.min_value == other.min_value and \
               self.max_value == other.max_value

    def evaluate(self, **kwargs):
        return Roll(self, **kwargs)


@RandomElement.register_dice
class Dice(RandomElement):
    """A group of dice, all with the same number of sides"""

    SEPERATOR = 'd'

    def __init__(self, amount, max_value, min_value=1):
        super(Dice, self).__init__(amount, min_value, max_value)
        self.original_operands = (amount, max_value)

    @property
    def sides(self):
        return self.max_value

    def __repr__(self):
        p = '{0!r}, {1!r}'.format(self.amount, self.max_value)
        if self.min_value != 1:
            p += ', {0!r}'.format(self.min_value)
        return "{}({})".format(classname(self), p)

    def __str__(self):
        return "{0!s}{1}{2!s}".format(self.amount, self.SEPERATOR, self.sides)


@RandomElement.register_dice
class WildDice(Dice):
    "A group of dice with the last being explodable or a failure mode on 1"

    SEPERATOR = 'w'

    def evaluate(self, **kwargs):
        return WildRoll(self, **kwargs)


@RandomElement.register_dice
class FudgeDice(Dice):
    "A group of dice whose sides range from -x to x, including 0"

    SEPERATOR = 'u'

    def __init__(self, amount, range):
        super(FudgeDice, self).__init__(amount, range, -range)

    def __repr__(self):
        p = '{0!r}, {1!r}'.format(self.amount, self.max_value)
        if self.min_value != -self.max_value:
            p += ', {0!r}'.format(self.min_value)
        return "{}({})".format(classname(self), p)


class Operator(Element):
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
            try:
                self.rhs_index = -1
                value = self.function(*self.operands)
            except TypeError:
                value = self.operands[0]

                for i, o in enumerate(self.operands[1:]):
                    self.rhs_index = i
                    value = self.function(value, o)

            if hasattr(self.__class__, 'output_cls'):
                return self.evaluate_object(value, self.output_cls, **kwargs)
            return value

        except ZeroDivisionError:
            zero = self.operands[1:].index(0) + 1
            zero_op = self.original_operands[zero]
            offset = zero_op.location - self.location
            msg = "Division by zero"
            if not isinstance(zero_op, int):
                msg += ' (%s evaluated to 0)' % zero_op
            raise self.fatal(msg, offset=offset)

    @property
    def function(self):
        raise NotImplementedError("Operator subclass has no function")


class IntegerOperator(Operator):
    def preprocess_operands(self, *operands, **kwargs):
        def eval_wrapper(operand):
            return self.evaluate_object(operand, Integer, **kwargs)

        return [eval_wrapper(o) for o in operands]


class RHSIntegerOperator(IntegerOperator):
    "Like IntegerOperator, but doesn't transform the left operator to an int"
    def preprocess_operands(self, *operands, **kwargs):
        ret = [self.evaluate_object(operands[0], **kwargs)]
        for operand in operands[1:]:
            ret.append(self.evaluate_object(operand, Integer, **kwargs))
        return ret


class Div(IntegerOperator):
    output_cls = Integer
    function = operator.floordiv


class Mul(IntegerOperator):
    output_cls = Integer
    function = operator.mul


class Sub(IntegerOperator):
    output_cls = Integer
    function = operator.sub


class Add(IntegerOperator):
    output_cls = Integer
    function = operator.add


class Modulo(IntegerOperator):
    function = operator.mod


class AddEvenSubOdd(Operator):
    function = addevensubodd


class Total(Operator):
    output_cls = Integer
    function = sum


class Successes(RHSIntegerOperator):
    def function(self, iterable, thresh):
        if not isinstance(iterable, IntegerList):
            iterable = (iterable,)
        elif isinstance(iterable, Roll):
            max_value = iterable.random_element.max_value
            if isinstance(max_value, RandomElement):
                raise self.fatal("Nested dice in success not yet supported.",
                                 location=max_value.location)
            if thresh > iterable.random_element.max_value:
                raise self.fatal("Success threshold higher than roll result.")
        return sum(x >= thresh for x in iterable)


class SuccessFail(RHSIntegerOperator):
    def function(self, iterable, thresh):
        result = 0
        if not isinstance(iterable, IntegerList):
            iterable = (iterable,)
        elif isinstance(iterable, Roll):
            max_value = iterable.random_element.max_value
            if isinstance(max_value, RandomElement):
                raise self.fatal("Nested dice in success not yet supported.",
                                 location=max_value.location)
            if thresh > iterable.random_element.max_value:
                raise self.fatal("Success threshold higher than maximum roll "
                                 "result.")

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


class Again(RHSIntegerOperator):
    def function(self, lhs, rhs=None):

        if not isinstance(lhs, IntegerList):
            lhs = IntegerList([lhs])

        if rhs is None:
            if not isinstance(lhs, Roll):
                raise self.fatal('%s is not a random element' % lhs)

            rhs = lhs.random_element.max_value

        ret = lhs.copy()
        ret.clear()

        for elem in lhs:
            ret.append(elem)
            if elem == rhs:
                ret.append(elem)

        return ret


class Sort(Operator):
    def function(self, iterable):
        if not isinstance(iterable, IntegerList):
            raise self.fatal("Cannot sort %s!" % iterable)
        iterable = iterable.copy()
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


# TODO: stable removal instead of sort -> slice -> shuffle
class Lowest(RHSIntegerOperator):
    def function(self, iterable, n=None):
        if not isinstance(iterable, IntegerList):
            raise self.fatal("Can't take the lowest values of a scalar!")
        if n is None:
            n = len(iterable) - 1

        iterable = iterable.copy()
        iterable.sort()
        iterable[n:] = []
        random.shuffle(iterable)
        return iterable


class Highest(RHSIntegerOperator):
    def function(self, iterable, n=None):
        if not isinstance(iterable, IntegerList):
            raise self.fatal("Can't take the highest values of a scalar!")
        if n is None:
            n = len(iterable) - 1

        iterable = iterable.copy()
        iterable.sort()
        iterable[:-n] = []
        random.shuffle(iterable)
        return iterable


class Middle(RHSIntegerOperator):
    def function(self, iterable, n=None):
        if not isinstance(iterable, IntegerList):
            raise self.fatal("Can't take the middle values of a scalar!")
        num = len(iterable)
        if n is None:
            n = (num - 2) if num > 2 else 1
        elif n <= 0:
            n += num

        num_remove = num - n
        upper = num_remove // 2
        lower = num_remove - upper

        iterable = iterable.copy()
        iterable.sort()
        iterable[:lower], iterable[-upper:] = [], []
        random.shuffle(iterable)
        return iterable


class Explode(RHSIntegerOperator):
    def function(self, roll, thresh=None):
        if not isinstance(roll, Roll):
            raise self.fatal('Cannot explode {0}'.format(roll))
        elif thresh is None:
            thresh = roll.random_element.max_value

        if roll.random_element.min_value == roll.random_element.max_value:
            raise self.fatal('Cannot explode a roll of one-sided dice.')

        elif thresh <= roll.random_element.min_value:
            offset = 0
            orig_thresh = self.original_operands[self.rhs_index]

            if thresh is not None:
                offset = orig_thresh.location - self.location

            msg = ('Refusing to explode with threshold less than or equal to '
                   'the lowest possible roll.')

            if type(orig_thresh) is not Integer:
                msg += ' (%s evaluated to %s)' % (orig_thresh, thresh)

            raise self.fatal(msg, offset=offset)

        explosions = 0
        result = list(roll)
        rerolled = roll

        while rerolled:
            explosions += 1
            if explosions >= MAX_EXPLOSIONS:
                raise self.fatal('Too many explosions!')

            num_rerolls = sum(x >= thresh for x in rerolled)
            rerolled = roll.do_roll(num_rerolls)
            result.extend(rerolled)

        return ExplodedRoll(roll.random_element, rolled=result)


class Reroll(RHSIntegerOperator):
    def function(self, roll, thresh=None):
        if not isinstance(roll, Roll):
            raise self.fatal('Cannot reroll {0}'.format(roll))

        elem = roll.random_element

        if isinstance(elem.min_value, RandomElement):
            raise self.fatal("Nested dice in reroll not yet supported.",
                             location=elem.min_value.location)

        if thresh is None:
            thresh = elem.min_value

        roll = Roll(elem, rolled=roll, force_extreme=roll.force_extreme)

        for i, x in enumerate(roll):
            if x <= thresh:
                roll[i] = roll.do_roll_single()

        return roll


class ForceReroll(RHSIntegerOperator):
    def function(self, roll, thresh=None, force_min=False):
        if not isinstance(roll, Roll):
            raise self.fatal('Cannot reroll {0}'.format(roll))

        elem = roll.random_element

        if isinstance(elem.max_value, RandomElement):
            raise self.fatal("Nested dice in force-reroll not yet supported.",
                             location=elem.max_value.location)

        if thresh is None:
            thresh = elem.min_value

        max_min = min((elem.max_value, thresh + 1))

        roll = Roll(elem, rolled=roll, force_extreme=roll.force_extreme)

        for i, x in enumerate(roll):
            if x <= thresh:
                roll[i] = roll.do_roll_single(min_value=max_min)

        return roll


class Identity(Operator):
    # no function defined because of passthrough __new__
    def __new__(self, x):
        return x


class Negate(Operator):
    def __new__(cls, x):
        if isinstance(x, int):
            # Passthrough to prevent Negate() clutter
            return Integer(-x)
        return super(Negate, cls).__new__(cls)

    def function(self, operand):
        operand = IntegerList(operand)

        for i, x in enumerate(operand):
            operand[i] = -x

        return operand


class ArrayAdd(RHSIntegerOperator):
    def function(self, iterable, scalar):
        try:
            scalar = int(scalar)
            iterable = IntegerList(iterable)

            for i, x in enumerate(iterable):
                iterable[i] = x + scalar

            return iterable
        except TypeError:
            raise self.fatal('Invalid operands for array add')


class ArraySub(RHSIntegerOperator):
    def function(self, iterable, scalar):
        try:
            scalar = int(scalar)
            iterable = IntegerList(iterable)

            for i, x in enumerate(iterable):
                iterable[i] = x - scalar

            return iterable
        except TypeError:
            raise self.fatal('Invalid operands for array sub')
