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

import argparse

import dice
import dice.exceptions

__version__ = "dice v{0} by {1}.".format(dice.__version__, dice.__author__)

parser = argparse.ArgumentParser(
    prog="dice", description="Parse and evaluate dice notation.", epilog=__version__
)
parser.add_argument(
    "-m",
    "--min",
    action="store_true",
    help="Make all rolls the lowest possible result.",
)
parser.add_argument(
    "-M",
    "--max",
    action="store_true",
    help="Make all rolls the highest possible result.",
)
parser.add_argument(
    "-D",
    "--max-dice",
    action="store",
    type=int,
    metavar="N",
    help="Set the maximum number of dice per element.",
)
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Show additional output."
)
parser.add_argument(
    "-V",
    "--version",
    action="version",
    version=__version__,
    help="Show the package version.",
)
parser.add_argument(
    "expression",
    nargs="+",
    help="One or more expressions in dice notation",
)


def main(args=None):
    """Run roll() from a command line interface"""
    args = parser.parse_args(args=args)
    f_kwargs = {}

    if args.min:
        f_roll = dice.roll_min
    elif args.max:
        f_roll = dice.roll_max
    else:
        f_roll = dice.roll

    if args.max_dice:
        f_kwargs["max_dice"] = args.max_dice

    f_expr = " ".join(args.expression)

    try:
        roll, kwargs = f_roll(f_expr, raw=True, return_kwargs=True, **f_kwargs)

        if args.verbose:
            print("Result: ", end="")

        print(str(roll.evaluate_cached(**kwargs)))

        if args.verbose:
            print("Breakdown:")
            print(dice.utilities.verbose_print(roll, **kwargs))
    except dice.exceptions.DiceBaseException as e:
        print("Whoops! Something went wrong:")
        print(e.pretty_print())
        exit(1)
