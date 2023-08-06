from random import Random


class Die:

    def __init__(self, sides=6, seed=None):
        self.sides = sides
        self.r = Random(seed)

    def roll(self):
        return self.r.randint(1, self.sides)
