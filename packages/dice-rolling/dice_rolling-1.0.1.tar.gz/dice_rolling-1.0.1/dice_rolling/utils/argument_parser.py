import argparse
import re

from dice_rolling import __version__


class ParsingResult:
    def __init__(self):
        self.n_dice = 0
        self.n_sides = 0
        self.seed = None


def request_type(arg):
    regex = re.compile(r'^(\d+)d(\d+)$')
    if not regex.match(arg):
        raise argparse.ArgumentParser
    return arg


class ArgumentParser(argparse.ArgumentParser):

    def __init__(self):
        super().__init__(
            description="Dice roller.",
            add_help=True
        )

        self.add_argument('request', type=request_type)
        self.add_argument('-s', '--seed', dest='seed', default=None)
        self.add_argument(
            '-v', '--version',
            action='version', version=__version__
        )

    def parse(self):
        args = self.parse_args()
        result = ParsingResult()

        regex_result = re.search(r'^(\d+)d(\d+)$', args.request, re.IGNORECASE)

        result.n_dice = int(regex_result.group(1))
        result.n_sides = int(regex_result.group(2))

        if result.n_sides == 0:
            import sys
            print("A dice must have at least one side.", file=sys.stderr)
            exit(3)

        if args.seed:
            result.seed = int(args.seed)

        return result
