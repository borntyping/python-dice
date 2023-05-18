# dice

A Python library and command line tool for parsing and evaluating dice notation.

_I consider this library "finished", and don't expect to add any more features to it. Bug and security fixes may still be released, especially if you find any bugs after all this time. If you're interested in other libraries in this space, [dyce] has [a great comparison table][comparison-to-alternatives] of Python dice rolling libraries._

[dyce]: https://posita.github.io/dyce/latest/
[comparison-to-alternatives]: https://posita.github.io/dyce/0.6/#comparison-to-alternatives

## Quickstart

### Command-line

```shell
$ roll 3d6
```

The command line arguments are as follows:

* `-m` `--min` Make all rolls the lowest possible result
* `-M` `--max` Make all rolls the highest possible result
* `-h` `--help` Show this help text
* `-v` `--verbose` Show additional output
* `-V` `--version` Show the package version

If your expression begins with a dash (`-`), then put a double dash (`--`)
before it to prevent the parser from trying to process it as a command option.
Example: `roll -- -10d6`. Alternatively, use parenthesis: `roll (-10d6)`.

### Python API

Invoking from python:

```python
import dice
dice.roll('3d6')
```

This returns an `Element` which is the result of the roll, which can be a
`list`, `int`, or subclass thereof, depending on the top-level operator.

## Usage

### Installation

This library is available as `dice` on PyPI. Install it with your Python
package or dependency manager of choice — if you're installing it as a
command-line tool, I recommend [pipx].

A recent version of Python 3 (3.8 or above) is required. You can probably run
it or easily adapt it for older versions of Python, but I don't support any
end-of-life Python versions. Beyond that, the only dependency is the `pyparsing` library.

[pipx]: https://pypa.github.io/pipx/

### Notation

The expression works like a simple equation parser with some extra operators.

*The following operators are listed in order of precedence. Parentheses may
be used to force an alternate order of evaluation.*

The dice (`[N]dS`) operator takes an amount (N) and a number of sides (S), and
returns a list of N random numbers between 1 and S. For example: `4d6` may
return `[6, 3, 2, 4]`. Using a `%` as the second operand is shorthand for 
rolling a d100, and a using `f` is shorthand for ±1 fudge dice.

The fudge dice (`[N]uS`) operator is interchangeable with the dice operator,
but makes the dice range from -S to S instead of 1 to S. This includes 0.

A wild dice (`[N]wS`) roll is special. The last roll in this set is called the
"wild die". If this die's roll is the maximum value, the second-highest roll
in the set is set to the maximum value. If its roll is the minimum, then
both it and the highest roll in the set aer set to zero. Then another die is
rolled. If this roll is the minimum value again, then ALL die are set to zero.
If a single-sided wild die is rolled, the roll behaves like a normal one.

If N is not specified, it is assumed you want to roll a single die.
`d6` is equivalent to `1d6`.

Rolls can be exploded with the `x` operator, which adds additional dice
to the set for each roll above a given threshold. If a threshold isn't given,
it defaults to the maximum possible roll. If the extra dice exceed this
threshold, they "explode" again! Safeguards are in place to prevent this from
crashing the parser with infinite explosions.

You can make the parser re-roll dice below a certain threshold with the `r`
and `rr` operators. The single `r` variety allows the new roll to be below
the threshold, whereas the double variety's roll *changes* the roll range to
have a minimum of the threshold. The threshold defaults to the minimum roll.

The highest, middle or lowest rolls or list entries can be selected with
(`^` or `h`), (`m` or `o`), or (`v` or `l`) respectively.
`6d6^3` will keep the highest 3 rolls, whereas `6d6v3` will select
the lowest 3 rolls. If a number isn't specified, it defaults to keeping all
but one for highest and lowest, and all but two for the middle. If a negative
value is given as the operand for any of these operators, this operation will
drop that many elements from the result. For example, `6d6^-2` will drop the
two lowest values from the set, leaving the 4 highest. Zero has no effect.

A variant of the "explode" operator is the `a` ("again") operator. Instead of
re-rolling values equal to or greater than the threshold (or max value), this
operator doubles values *equal* to the provided threshold (or max value). When
no right-side operand is specified, the left side must be a dice expression.

There are two operators for taking a set of rolls or numbers and counting the
number of elements at or above a certain threshold, or "successes". Both
require a right-hand operand for the threshold. The first, `e`, only counts
successes. The second, `f`, counts successes minus failures, which are when
a roll is the minimum possible value for the die element, or 1 for lists.

A list or set of rolls can be turned into an integer with the total (`t`)
operator. `6d1t` will return `6` instead of `[1, 1, 1, 1, 1, 1]`.
Applying integer operations to a list of rolls will total them automatically.

A set of dice rolls can be sorted with the sort (`s`) operator. `4d6s`
will not change the return value, but the dice will be sorted from lowest to
highest.

The `+-` operator is a special prefix for sets of rolls and lists. It
negates odd roles within a list. Example: `[1, 2, 3]` -> `[-1, 2, -3]`.
There is also a negate (`-`) operator, which works on either single
elements, sets or rolls, or lists. There is also an identity `+` operator.

Values can be added or subtracted from each element of a list or set of rolls
with the point-wise add (`.+`) and subtract (`.-`) operators. For example:
`4d1 .+ 3` will return `[4, 4, 4, 4]`.

Basic integer operations are also available: `(16 / 8 * 4 - 2 + 1) % 4 -> 3`.


Finally, there are two operators for building and extending lists. To build a
list, use a comma to separate elements. If any comma-seperated item isn't a
scalar (e.g. a  roll), it is flattened into one by taking its total. The
"extend" operator (`|`) is used to merge two lists into one, or append single
elements to the beginning or end of a list.

### Python API

The calls to `dice.roll()` above may be replaced with `dice.roll_min()` or
`dice.roll_max()` to force ALL rolls to their highest or lowest values
respectively. This might be useful to see what the minimum and maximum
possible values for a given expression are. Beware that this causes wild dice
rolls to act like normal ones, and rolls performed as explosions are not
forced high or low.

The `roll()` function and variants take a boolean `raw` parameter which
makes the library return the element instead of the result. Note that the 
`evaluate_cached` method is called as part of `roll()`, which populates
`element.result`. Calling `element.evaluate()` will not reset this value.

To display a verbose breakdown of the element tree, the
`dice.utilities.verbose_print(element)` function is available.
If `element.result` has not yet been populated, the function calls
`evaluate_cached()` first. Keep this in mind if you want to print the result
of an evaluation with custom arguments. `verbose_print()` returns a `str`.

Most evaluation errors will raise `DiceError` or `DiceFatalError`, both of
which are subclasses of `DiceBaseError`. These exceptions have a method
named `pretty_print`, which will output a string indicating where the error
happened::

```python-repl
>>> try:
...   dice.roll('1/0')
... except dice.DiceBaseException as e:
...   print(e.pretty_print())
...
1/0
  ^ Division by zero
>>>
```
