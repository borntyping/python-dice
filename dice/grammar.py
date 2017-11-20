"""
Dice notation grammar

PyParsing is patched to make it easier to work with, by removing features
that get in the way of development and debugging. See the dice.utilities
module for more information.
"""

from __future__ import absolute_import, print_function, unicode_literals

from pyparsing import (CaselessLiteral, Forward, Literal, OneOrMore,
                       StringStart, StringEnd, Suppress, Word, nums, opAssoc)

from dice.elements import (Integer, FudgeDice, Successes, Mul, Div, Sub, Add,
                           AddEvenSubOdd, Total, Sort, Lowest, Middle, Highest,
                           Array, Extend, Explode, Reroll, ForceReroll, Negate,
                           WildDice, SuccessFail, Identity, ArrayAdd, ArraySub)

from dice.utilities import (patch_pyparsing, dice_select_unary,
                            dice_select_binary)

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
            elif arity == 2:
                operator_expression = last + OneOrMore(new_this)

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

dice_element = CaselessLiteral('d').suppress()
special = Literal('%') | CaselessLiteral('f')

# An expression in dice notation
expression = StringStart() + operatorPrecedence(integer, [
    (dice_element, 2, opAssoc.LEFT, dice_select_binary, special),
    (dice_element, 1, opAssoc.RIGHT, dice_select_unary, special),

    (CaselessLiteral('u').suppress(), 2, opAssoc.LEFT, FudgeDice.parse),
    (CaselessLiteral('u').suppress(), 1, opAssoc.RIGHT, FudgeDice.parse_unary),

    (CaselessLiteral('w').suppress(), 2, opAssoc.LEFT, WildDice.parse),
    (CaselessLiteral('w').suppress(), 1, opAssoc.RIGHT, WildDice.parse_unary),

    (CaselessLiteral('x').suppress(), 2, opAssoc.LEFT, Explode.parse),
    (CaselessLiteral('x').suppress(), 1, opAssoc.LEFT, Explode.parse),
    (CaselessLiteral('rr').suppress(), 2, opAssoc.LEFT, ForceReroll.parse),
    (CaselessLiteral('rr').suppress(), 1, opAssoc.LEFT, ForceReroll.parse),
    (CaselessLiteral('r').suppress(), 2, opAssoc.LEFT, Reroll.parse),
    (CaselessLiteral('r').suppress(), 1, opAssoc.LEFT, Reroll.parse),

    (Word('^hH', exact=1).suppress(), 2, opAssoc.LEFT, Highest.parse),
    (Word('^hH', exact=1).suppress(), 1, opAssoc.LEFT, Highest.parse),
    (Word('vlL', exact=1).suppress(), 2, opAssoc.LEFT, Lowest.parse),
    (Word('vlL', exact=1).suppress(), 1, opAssoc.LEFT, Lowest.parse),
    (Word('oOmM', exact=1).suppress(), 2, opAssoc.LEFT, Middle.parse),
    (Word('oOmM', exact=1).suppress(), 1, opAssoc.LEFT, Middle.parse),
    (CaselessLiteral('e').suppress(), 2, opAssoc.LEFT, Successes.parse),
    (CaselessLiteral('f').suppress(), 2, opAssoc.LEFT, SuccessFail.parse),

    (Literal('+-').suppress(), 1, opAssoc.RIGHT, AddEvenSubOdd.parse),
    (Literal('+').suppress(), 1, opAssoc.RIGHT, Identity.parse),
    (Literal('-').suppress(), 1, opAssoc.RIGHT, Negate.parse),

    (CaselessLiteral('t').suppress(), 1, opAssoc.LEFT, Total.parse),
    (CaselessLiteral('s').suppress(), 1, opAssoc.LEFT, Sort.parse),

    (Literal('.+').suppress(), 2, opAssoc.LEFT, ArrayAdd.parse),
    (Literal('.-').suppress(), 2, opAssoc.LEFT, ArraySub.parse),

    (Literal('/').suppress(), 2, opAssoc.LEFT, Div.parse),
    (Literal('*').suppress(), 2, opAssoc.LEFT, Mul.parse),
    (Literal('-').suppress(), 2, opAssoc.LEFT, Sub.parse),
    (Literal('+').suppress(), 2, opAssoc.LEFT, Add.parse),

    (Literal(',').suppress(), 2, opAssoc.LEFT, Array.parse),
    (Literal('|').suppress(), 2, opAssoc.LEFT, Extend.parse),
]) + StringEnd()
expression.setName("expression")
