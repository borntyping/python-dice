from __future__ import absolute_import, unicode_literals, division
from operator import mul

from pyparsing import CaselessLiteral, Or, replaceWith, Optional, ZeroOrMore, Word, nums

def literal(item):
    name, value = item
    literal = CaselessLiteral(name)
    literal.setName(name)
    literal.setParseAction(replaceWith(value))
    return literal

def literals(dictionary):
    return Or(map(literal, dictionary.items()))

units = literals({
    'zero': 0,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
})

tens = literals({
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90,
})

major = literals({
    'hundred': 100,
    'thousand': int(1e3),
    'million': int(1e6),
    'billion': int(1e9),
})

major_number = (units + major)
major_number.setParseAction(lambda tokens: reduce(mul, tokens))

text_number = ZeroOrMore(major_number) + Optional(tens) + Optional(units)
text_number.ignore(CaselessLiteral("and"))
text_number.ignore(CaselessLiteral(","))
text_number.setParseAction(sum)
text_number.setName("text number")

integer = Word(nums)
integer.setParseAction(int)
integer.setName("integer")

number = text_number | integer
number.setName("number")
