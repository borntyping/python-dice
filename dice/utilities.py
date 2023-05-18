import dice.elements
from dice.constants import VERBOSE_INDENT


def classname(obj):
    """Returns the name of an objects class"""
    return obj.__class__.__name__


def single(iterable):
    """Returns a single item if the iterable has only one item"""
    return iterable[0] if len(iterable) == 1 else iterable


def wrap_string(cls, *args, **kwargs):
    suppress = kwargs.pop("suppress", True)
    e = cls(*args, **kwargs)
    e.setParseAction(dice.elements.String.parse)
    if suppress:
        return e.suppress()
    return e


def add_even_sub_odd(operator, operand):
    """Add even numbers, subtract odd ones. See http://1w6.org/w6"""
    try:
        for i, x in enumerate(operand):
            if x % 2:
                operand[i] = -x
        return operand
    except TypeError:
        if operand % 2:
            return -operand
        return operand


def dice_switch(amount, dice_type, kind="d"):
    kind = kind.lower()
    if len(kind) != 1:
        raise ValueError("Dice operator must be 1 letter", 1)

    if isinstance(dice_type, int) and int(dice_type) < 1:
        raise ValueError("Number of sides must be one or more", 2)
    elif isinstance(dice_type, str):
        dice_type = dice_type.lower()

    if dice_type == "f":
        if kind not in ("d", "u"):
            raise ValueError("can only use dF or uF", 2)
        return dice.elements.FudgeDice(amount, 1)
    elif kind not in dice.elements.RandomElement.DICE_MAP:
        raise ValueError("unknown dice kind: %s" % kind, 1)

    random_element = dice.elements.RandomElement.DICE_MAP[kind]

    if str(dice_type) == "%":
        dice_type = 100

    return random_element(amount, dice_type)


def verbose_print_op(element, depth=0):
    lines = [[depth, classname(element) + "("]]
    num_ops = len(element.original_operands)

    for i, e in enumerate(element.original_operands):
        newlines = verbose_print_sub(e, depth + 1)

        if len(newlines) > 1 or num_ops > 1:
            if i + 1 < num_ops:
                newlines[-1].append(",")
            lines.extend(newlines)
        else:
            lines[-1].extend(newlines[0][1:])

    closing = ") -> %s" % element.result

    if num_ops > 1 or len(lines) > 1 and lines[-1][0] < lines[-2][0]:
        lines.append([depth, closing])
    else:
        lines[-1].append(closing)

    return lines


def verbose_print_sub(element, indent=0, **kwargs):
    lines = []
    if isinstance(element, dice.elements.Element) and not hasattr(element, "result"):
        element.evaluate_cached(**kwargs)

    if isinstance(element, dice.elements.Operator):
        return verbose_print_op(element, indent)

    elif isinstance(element, dice.elements.Dice):
        if any(
            not isinstance(op, (dice.elements.Integer, int))
            for op in element.original_operands
        ):
            return verbose_print_op(element, indent)

        line = "roll %s -> %s" % (element, element.result)
    else:
        line = str(element)

    lines.append([indent, line])
    return lines


def verbose_print(element, **kwargs):
    lines = verbose_print_sub(element, **kwargs)
    lines = [(" " * (VERBOSE_INDENT * t[0]) + "".join(t[1:])) for t in lines]
    return "\n".join(lines)
