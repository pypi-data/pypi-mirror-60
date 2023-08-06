import argparse
import re
from contextlib import suppress
from typing import Any

from dice_rolling import __version__


class ParsingResult:
    """Class to contain the full parsed arguments.
    """

    def __init__(self, request: str):
        """Constructor of ParsingResult.
        """
        self.n_dice = 1
        self.n_sides = 0
        self.addition = 0
        self.keep = 0
        self.seed = None
        self.full_request = request

    def __setattr__(self, key: str, value: Any) -> None:
        """Overwritten method to set an attribute. This is done to cast the value to
        integer if possible."""
        if value or value == 0:
            # Set the value to the attribute if the value is not None.
            with suppress(ValueError):
                value = int(value)
            super().__setattr__(key, value)

        elif key in ['seed']:
            # If the key is in the list of allowed keys to be set as None, set it.
            # The other attributes will not update its value in this case.
            super().__setattr__(key, None)


def request_type(arg: str) -> str:
    """Function to make sure that the roll requested is valid and compliant with the
    regex ArgumentParser.REQUEST_REGEX.
    """
    if not re.compile(ArgumentParser.REQUEST_REGEX).match(arg):
        raise argparse.ArgumentParser
    return arg


class ArgumentParser(argparse.ArgumentParser):
    """Class to handle the parsing of the arguments received on the CLI.
    """

    """Regex to allow only the implemented dice notation."""
    REQUEST_REGEX = r'^(\d*)d(\d+)(?:\+(\d+))?(k(h|l)\d+)?$'

    def __init__(self):
        """Constructor of ArgumentParser. Sets the allowed arguments."""
        super().__init__(description="Dice roller.", add_help=True)

        self.add_argument(
            'request', type=request_type,
            help="roll description with modifiers, for instance, 3d6+2"
        )
        self.add_argument(
            '-s', '--seed', dest='seed', default=None,
            help="dice's seed for testing purposes"
        )
        self.add_argument('-v', '--version', action='version', version=__version__)

    def parse(self) -> ParsingResult:
        """Method to parse the arguments and retrieve the actions of the roll.

        :returns: The result of the parsing.
        """

        args = self.parse_args()
        result = ParsingResult(args.request)

        # Apply the regex to the received argument to extract the values as groups.
        regex_result = re.search(self.REQUEST_REGEX, args.request, re.IGNORECASE)

        # Set the extracted values.
        result.n_dice = regex_result.group(1)
        result.n_sides = regex_result.group(2)
        result.addition = regex_result.group(3)

        # Set the number of kept dice, if applies.
        keep = regex_result.group(4)
        if keep:
            result.keep = int(keep[2:]) * (1 if keep[1] == 'h' else -1)

        if result.n_sides == 0:
            # The program must have at least one side per die.
            import sys
            print("A dice must have at least one side.", file=sys.stderr)
            exit(3)

        if args.seed:
            # If a seed has been provided, extract it.
            result.seed = int(args.seed)

        return result
