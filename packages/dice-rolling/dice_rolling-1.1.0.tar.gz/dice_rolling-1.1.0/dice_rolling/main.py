from dice_rolling import RollBuilder
from dice_rolling.utils.argument_parser import ArgumentParser


def main():
    """Entry point of the CLI command.
    """

    # Parse the arguments.
    args = ArgumentParser().parse()

    # Create the builder and execute it.
    b = RollBuilder(args.seed)
    b.set_amount_of_dice(args.n_dice)
    b.set_number_of_sides(args.n_sides)
    b.addition_to_roll(args.addition)
    b.keep_n(args.keep)
    b.build()

    # Send the full result to stdout.
    result = b.get_full_result()

    if not result[2]:
        print(f"Rolled {args.full_request} and got {result[0]}. {result[1]}")
    else:
        print(f"Rolled {args.full_request} and got {result[0]}. "
              f"Kept {result[1]} and discarded {result[2]}.")


if __name__ == "__main__":
    main()
