"""
Usage:
    roll [--verbose] [--min | --max] [--] <expression>...

Options:
    -m --min        Make all rolls the lowest possible result
    -M --max        Make all rolls the highest possible result
    -h --help       Show this help text
    -v --verbose    Show additional output
    -V --version    Show the package version
"""

from __future__ import absolute_import, print_function, unicode_literals

import docopt

import dice

__version__ = "dice v{0} by {1}".format(dice.__version__, dice.__author__)


def main(argv=None):
    """Run roll() from a command line interface"""
    args = docopt.docopt(__doc__, argv=argv, version=__version__)
    verbose = bool(args['--verbose'])

    f_roll = dice.roll

    if args['--min']:
        f_roll = dice.roll_min
    elif args['--max']:
        f_roll = dice.roll_max

    expr = ' '.join(args['<expression>'])
    roll, kwargs = f_roll(expr, raw=True, return_kwargs=True)

    if verbose:
        print('Result: ', end='')

    print(str(roll.evaluate_cached(**kwargs)))

    if verbose:
        print('Breakdown:')
        print(dice.utilities.verbose_print(roll, **kwargs))
