from typing import Any, Tuple

from dice_rolling import Die


class RollBuilder:
    """Class to build a complete throw of the dice.
    """

    def __init__(self, seed: Any = None):
        """Constructor of RollBuilder.

        :param Any seed: Seed for the dice, if any.
        """
        self.__n_dice = 1
        self.__n_sides = 0
        self.__addition = 0
        self.__keep = 0
        self.__rolls = []
        self.__discarded = []

        Die.set_seed(seed)

    def set_amount_of_dice(self, n_dice: int) -> None:
        """Method to set the amount of dice.

        :param int n_dice: Amount of dice.
        """
        self.__n_dice = n_dice

    def set_number_of_sides(self, n_sides: int) -> None:
        """Method to set the number of sides of the dice.

        :param int n_sides: Number of sides of the dice.
        """
        self.__n_sides = n_sides

    def addition_to_roll(self, addition: int) -> None:
        """Method to set the amount to add to every rolled die.

        :param int addition: Amount to add.
        """
        self.__addition += addition

    def keep_n(self, n_items: int) -> None:
        """Method to set the number and preference to keep after every die has been
        rolled.

        - If n_items > 0: It will keep the highest n_items.
        - If n_items < 0: It will keep the lowest n_items.

        :param int n_items: Number and preference to keep.
        """
        if abs(n_items) <= self.__n_dice:
            self.__keep = n_items

    def build(self) -> None:
        """Method to build the complete throw of the dice after every parameter
        has been set.
        """
        self.__rolls = []
        for i in range(self.__n_dice):
            self.__rolls.append(
                Die(self.__n_sides).roll() + self.__addition
            )

        if self.__keep:
            sort = sorted(self.__rolls, reverse=self.__keep > 0)
            self.__rolls = sort[:self.__keep]
            self.__discarded = sort[self.__keep:]

    def get_result(self) -> list:
        """Method to obtain the kept results of the complete roll.

        The discarded dice are not included.

        :returns: The kept results of the complete roll.
        """
        return self.__rolls

    def get_full_result(self) -> Tuple[int, list, list]:
        """Method to obtain the full results of the complete roll.

        :returns: The full results of the full roll. The kept and the discarded rolls.
        """
        return sum(self.__rolls), self.__rolls, self.__discarded
