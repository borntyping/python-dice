"""
Usage:
    roll [--verbose] <expression>

Options:
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
    result = dice.roll(args['<expression>'], verbose=args['--verbose'])
    if args['--verbose']:
        print("Result:", end=" ")
    print(str(result))
