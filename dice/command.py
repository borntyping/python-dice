"""
Usage:
    roll [--verbose] [--min | --max] [--max-dice=<dice>] [--] <expression>...

Options:
    -m --min              Make all rolls the lowest possible result
    -M --max              Make all rolls the highest possible result
    -D --max-dice=<dice>  Set the maximum number of dice per element
    -h --help             Show this help text
    -v --verbose          Show additional output
    -V --version          Show the package version
"""

from __future__ import absolute_import, print_function, unicode_literals

import docopt

import dice
from dice.exceptions import DiceBaseException

__version__ = "dice v{0} by {1}".format(dice.__version__, dice.__author__)


def main(argv=None):
    """Run roll() from a command line interface"""
    args = docopt.docopt(__doc__, argv=argv, version=__version__)
    verbose = bool(args['--verbose'])

    f_roll = dice.roll
    kwargs = {}

    if args['--min']:
        f_roll = dice.roll_min
    elif args['--max']:
        f_roll = dice.roll_max

    if args['--max-dice']:
        try:
            kwargs['max_dice'] = int(args['--max-dice'])
        except ValueError:
            print("Invalid value for --max-dice: '%s'" % args['--max-dice'])
            exit(1)

    expr = ' '.join(args['<expression>'])

    try:
        roll, kwargs = f_roll(expr, raw=True, return_kwargs=True, **kwargs)

        if verbose:
            print('Result: ', end='')

        print(str(roll.evaluate_cached(**kwargs)))

        if verbose:
            print('Breakdown:')
            print(dice.utilities.verbose_print(roll, **kwargs))
    except DiceBaseException as e:
        print('Whoops! Something went wrong:')
        print(e.pretty_print())
        exit(1)
