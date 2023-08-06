# Dice rolling

This module aims to implement the throw of many types of dice.

## Installation

Simply run:

```bash
pip install dice_rolling
```

## CLI usage

Once installed, a throw of a simple die of 6 sides can be performed with:

```bash
roll 1d6
```

Or, for instance, to throw three 20-sided dice can be as simple as:

```bash
roll 3d20
```

## Module usage

To use this module you should use the class RollBuilder to implement the throws:

```python
from dice_rolling import RollBuilder

builder = RollBuilder()
builder.set_amount_of_dice(3)
builder.set_number_of_sides(20)
builder.build()

print(builder.get_result())
```

*More methods will be added to the builder in the future.*

## Throws

Currently it only supports the following throws:

- `x`d`y`: Where `x` is the number of dice and `y` the number of faces of each die.

