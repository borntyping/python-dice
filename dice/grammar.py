"""
Dice notation grammar

PyParsing is patched to make it easier to work with, by removing features
that get in the way of development and debugging. See the dice.utilities
module for more information.
"""

from __future__ import absolute_import, print_function, unicode_literals

from pyparsing import (CaselessLiteral, Forward, Literal, OneOrMore, Or,
                       StringStart, StringEnd, Suppress, Word, nums, opAssoc)

from dice.elements import (Integer, Successes, Mul, Div, Modulo, Sub, Add,
                           Identity, AddEvenSubOdd, Total, Sort, Lowest,
                           Middle, Highest, Array, Extend, Explode, Reroll,
                           ForceReroll, Negate, SuccessFail, ArrayAdd,
                           ArraySub, RandomElement, Again)

from dice.utilities import patch_pyparsing, wrap_string

patch_pyparsing()


def operatorPrecedence(base, operators):
    """
    This re-implements pyparsing's operatorPrecedence function.

    It gets rid of a few annoying bugs, like always putting operators inside
    a Group, and matching the whole grammar with Forward first (there may
    actually be a reason for that, but I couldn't find it). It doesn't
    support trinary expressions, but they should be easy to add if it turns
    out I need them.
    """

    # The full expression, used to provide sub-expressions
    expression = Forward()

    # The initial expression
    last = base | Suppress('(') + expression + Suppress(')')

    def parse_operator(expr, arity, association, action=None, extra=None):
        return expr, arity, association, action, extra

    for op in operators:
        # Use a function to default action to None
        expr, arity, association, action, extra = parse_operator(*op)

        # Check that the arity is valid
        if arity < 1 or arity > 2:
            raise Exception("Arity must be unary (1) or binary (2)")

        if association not in (opAssoc.LEFT, opAssoc.RIGHT):
            raise Exception("Association must be LEFT or RIGHT")

        # This will contain the expression
        this = Forward()

        # Create an expression based on the association and arity
        if association is opAssoc.LEFT:
            new_last = (last | extra) if extra else last
            if arity == 1:
                operator_expression = new_last + OneOrMore(expr)
            elif arity == 2:
                operator_expression = last + OneOrMore(expr + new_last)
        elif association is opAssoc.RIGHT:
            new_this = (this | extra) if extra else this
            if arity == 1:
                operator_expression = expr + new_this
            # Currently no operator uses this, so marking it nocover for now
            elif arity == 2:                                      # nocover
                operator_expression = last + OneOrMore(new_this)  # nocover

        # Set the parse action for the operator
        if action is not None:
            operator_expression.setParseAction(action)

        this <<= (operator_expression | last)
        last = this

    # Set the full expression and return it
    expression <<= last
    return expression


# An integer value
integer = Word(nums)
integer.setParseAction(Integer.parse)
integer.setName("integer")

dice_seperators = RandomElement.DICE_MAP.keys()
dice_element = Or(wrap_string(CaselessLiteral, x, suppress=False)
                  for x in dice_seperators)
special = wrap_string(Literal, '%', suppress=False) | \
          wrap_string(CaselessLiteral, 'f', suppress=False)

# An expression in dice notation
expression = StringStart() + operatorPrecedence(integer, [
    (dice_element, 2, opAssoc.LEFT, RandomElement.parse, special),
    (dice_element, 1, opAssoc.RIGHT, RandomElement.parse_unary, special),

    (wrap_string(CaselessLiteral, 'x'), 2, opAssoc.LEFT, Explode.parse),
    (wrap_string(CaselessLiteral, 'x'), 1, opAssoc.LEFT, Explode.parse),
    (wrap_string(CaselessLiteral, 'rr'), 2, opAssoc.LEFT, ForceReroll.parse),
    (wrap_string(CaselessLiteral, 'rr'), 1, opAssoc.LEFT, ForceReroll.parse),
    (wrap_string(CaselessLiteral, 'r'), 2, opAssoc.LEFT, Reroll.parse),
    (wrap_string(CaselessLiteral, 'r'), 1, opAssoc.LEFT, Reroll.parse),

    (wrap_string(Word, '^hH', exact=1), 2, opAssoc.LEFT, Highest.parse),
    (wrap_string(Word, '^hH', exact=1), 1, opAssoc.LEFT, Highest.parse),
    (wrap_string(Word, 'vlL', exact=1), 2, opAssoc.LEFT, Lowest.parse),
    (wrap_string(Word, 'vlL', exact=1), 1, opAssoc.LEFT, Lowest.parse),
    (wrap_string(Word, 'oOmM', exact=1), 2, opAssoc.LEFT, Middle.parse),
    (wrap_string(Word, 'oOmM', exact=1), 1, opAssoc.LEFT, Middle.parse),
    (wrap_string(CaselessLiteral, 'a'), 2, opAssoc.LEFT, Again.parse),
    (wrap_string(CaselessLiteral, 'a'), 1, opAssoc.LEFT, Again.parse),
    (wrap_string(CaselessLiteral, 'e'), 2, opAssoc.LEFT, Successes.parse),
    (wrap_string(CaselessLiteral, 'f'), 2, opAssoc.LEFT, SuccessFail.parse),

    (wrap_string(CaselessLiteral, 't'), 1, opAssoc.LEFT, Total.parse),
    (wrap_string(CaselessLiteral, 's'), 1, opAssoc.LEFT, Sort.parse),

    (wrap_string(Literal, '+-'), 1, opAssoc.RIGHT, AddEvenSubOdd.parse),
    (wrap_string(Literal, '+'), 1, opAssoc.RIGHT, Identity.parse),
    (wrap_string(Literal, '-'), 1, opAssoc.RIGHT, Negate.parse),

    (wrap_string(Literal, '.+'), 2, opAssoc.LEFT, ArrayAdd.parse),
    (wrap_string(Literal, '.-'), 2, opAssoc.LEFT, ArraySub.parse),

    (wrap_string(Literal, '%'), 2, opAssoc.LEFT, Modulo.parse),
    (wrap_string(Literal, '/'), 2, opAssoc.LEFT, Div.parse),
    (wrap_string(Literal, '*'), 2, opAssoc.LEFT, Mul.parse),
    (wrap_string(Literal, '-'), 2, opAssoc.LEFT, Sub.parse),
    (wrap_string(Literal, '+'), 2, opAssoc.LEFT, Add.parse),

    (wrap_string(Literal, ','), 2, opAssoc.LEFT, Array.parse),
    (wrap_string(Literal, '|'), 2, opAssoc.LEFT, Extend.parse),
]) + StringEnd()
expression.setName("expression")
