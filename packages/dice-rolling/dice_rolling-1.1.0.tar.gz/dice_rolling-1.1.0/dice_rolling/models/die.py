from random import Random
from typing import Any


class Die:
    """Class to represent a single die.

    All dice have the same random source in order to set a seed globally among them to
    later reproduce a throw.
    """
    rand = Random()

    def __init__(self, sides: int = 6):
        """Constructor of Die.

        :param int sides: Number of sides of the die. Defaults to 6.
        """
        self.sides = sides

    def roll(self) -> int:
        """Method to roll the die.

        :returns: The roll's result.
        """
        return self.rand.randint(1, self.sides)

    @classmethod
    def set_seed(cls, seed: Any) -> None:
        """Method to set a global seed for every die.
        """
        cls.rand = Random(seed)
