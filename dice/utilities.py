from __future__ import absolute_import, unicode_literals

import dice.elements
from dice.constants import VERBOSE_INDENT
import warnings
import pyparsing


def classname(obj):
    """Returns the name of an objects class"""
    return obj.__class__.__name__


def single(iterable):
    """Returns a single item if the iterable has only one item"""
    return iterable[0] if len(iterable) == 1 else iterable


def patch_pyparsing(packrat=True, arity=True):
    """Applies monkey-patches to pyparsing"""
    if packrat:
        enable_pyparsing_packrat()

    if arity:
        disable_pyparsing_arity_trimming()


def enable_pyparsing_packrat():
    """Enables pyparsing's packrat parsing, which is much faster for the type
    of parsing being done in this library"""
    warnings.warn("Enabled pyparsing packrat parsing", ImportWarning)
    pyparsing.ParserElement.enablePackrat()


def _trim_arity(func, maxargs=None):
    def wrapper(string, location, tokens):
        return func(string, location, tokens)
    return wrapper


def disable_pyparsing_arity_trimming():
    """When pyparsing encounters a TypeError when calling a parse action, it
    will keep trying the call the function with one less argument each time
    until it succeeds. This disables this functionality, as it catches
    TypeErrors raised by other functions and makes debugging those functions
    very hard to do."""
    warnings.warn("Disabled pyparsing arity trimming", ImportWarning)
    pyparsing._trim_arity = _trim_arity


def wrap_string(cls, *args, **kwargs):
    suppress = kwargs.pop('suppress', True)
    e = cls(*args, **kwargs)
    e.setParseAction(dice.elements.String.parse)
    if suppress:
        return e.suppress()
    return e


def addevensubodd(operator, operand):
    """Add even numbers, subtract odd ones. See http://1w6.org/w6 """
    try:
        for i, x in enumerate(operand):
            if x % 2:
                operand[i] = -x
        return operand
    except TypeError:
        if operand % 2:
            return -operand
        return operand


def dice_switch(amount, dicetype, kind='d'):
    DICE_MAP = dice.elements.RandomElement.DICE_MAP
    kind = kind.lower()
    if len(kind) != 1:
        raise ValueError("Dice operator must be 1 letter", 1)

    if isinstance(dicetype, int) and int(dicetype) < 1:
        raise ValueError("Number of sides must be one or more", 2)
    elif isinstance(dicetype, str):
        dicetype = dicetype.lower()

    if dicetype == 'f':
        if kind not in ('d', 'u'):
            raise ValueError("can only use dF or uF", 2)
        return dice.elements.FudgeDice(amount, 1)
    elif kind not in DICE_MAP:
        raise ValueError("unknown dice kind: %s" % kind, 1)

    random_element = DICE_MAP[kind]

    if str(dicetype) == '%':
        dicetype = 100

    return random_element(amount, dicetype)


def verbose_print_op(element, depth=0):
    lines = []
    lines.append([depth, classname(element) + '('])
    num_ops = len(element.original_operands)

    for i, e in enumerate(element.original_operands):
        newlines = verbose_print_sub(e, depth + 1)

        if len(newlines) > 1 or num_ops > 1:
            if i + 1 < num_ops:
                newlines[-1].append(',')
            lines.extend(newlines)
        else:
            lines[-1].extend(newlines[0][1:])

    closing = ') -> %s' % element.result

    if num_ops > 1 or len(lines) > 1 and lines[-1][0] < lines[-2][0]:
        lines.append([depth, closing])
    else:
        lines[-1].append(closing)

    return lines


def verbose_print_sub(element, indent=0, **kwargs):
    lines = []
    if isinstance(element, dice.elements.Element) and \
            not hasattr(element, 'result'):
        element.evaluate_cached(**kwargs)

    if isinstance(element, dice.elements.Operator):
        return verbose_print_op(element, indent)

    elif isinstance(element, dice.elements.Dice):
        if any(not isinstance(op, (dice.elements.Integer, int))
               for op in element.original_operands):
            return verbose_print_op(element, indent)

        line = 'roll %s -> %s' % (element, element.result)
    else:
        line = str(element)

    lines.append([indent, line])
    return lines


def verbose_print(element, **kwargs):
    lines = verbose_print_sub(element, **kwargs)
    lines = [(' ' * (VERBOSE_INDENT * t[0]) + ''.join(t[1:])) for t in lines]
    return '\n'.join(lines)
