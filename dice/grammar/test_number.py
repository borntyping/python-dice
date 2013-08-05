from __future__ import absolute_import, unicode_literals, division

from dice.grammar.number import number

values_units = {
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
}

values_tens = {
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90,
}

values_major = {
    'hundred': int(1e2),
    'thousand': int(1e3),
    'million': int(1e6),
    'billion': int(1e9),
}

def parse(expression):
    print(number.parseString(expression))
    return number.parseString(expression)[0]

def parse_all(format_string, units, value_func=lambda v: v):
    for unit, value in units.items():
        assert parse(format_string.format(unit)) == value_func(value)

def parse_two(format_string, value_func, units_one, units_two):
    """This could probably be done more intelligently"""
    for unit_one, value_one in units_one.items():
        for unit_two, value_two in units_two.items():
            expr = format_string.format(unit_one, unit_two)
            value = value_func(value_one, value_two)
            assert parse(expr) == value

def test_empty():
    """I have no idea how or why this works"""
    assert parse("") == 0

def test_x_hundred():
    parse_all("{0} hundred", values_units, lambda v: v * 100)

def test_one_hundred_and_x():
    parse_all("one hundred and {0}", values_tens, lambda v: v + 100)

def test_one_hundred_and_x_one():
    parse_all("one hundred and {0} one", values_tens, lambda v: v + 101)

def test_major():
    parse_all("one {0}", values_major)

def test_x_major():
    parse_two("{0} {1}", lambda u,m: u*m, values_units, values_major)

def test_full():
    assert parse("one thousand, one hundred and twenty three") == 1123
