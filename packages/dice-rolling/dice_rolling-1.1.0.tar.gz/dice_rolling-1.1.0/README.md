# Dice rolling

This module aims to implement the throw of many types of dice.

## Installation

Simply run:

```bash
pip install dice-rolling
```

## CLI usage

Once installed, a throw of a simple die of 6 sides can be performed with:

```bash
$ roll 1d6
Rolled 1d6 and got 4. [4]
```

Or, for instance, to throw three 20-sided dice can be as simple as:

```bash
$ roll 3d20
Rolled 3d20 and got 36. [14, 9, 13]
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


## Throws

The request must start with `x`d`y`, where `x` is the number of dice and `y` the number of faces of each die.

For example, to roll 4 6-sided dice:
```bash
$ roll 4d6
Rolled 4d6 and got 16. [5, 2, 3, 6]
```

After that, the following modifiers have been implemented
(using the previous result as reference):

- `+a`: Add the value of `a` to each die.
  For example, to roll 4 6-sided dice and add 3 to each roll:
  ```bash
  $ roll 4d6+3
  Rolled 4d6+3 and got 28. [8, 5, 6, 9]
  ```

- `khb`: `K`eep the `H`ighest `b`.
  For example, to roll 4 6-sided dice and keep the highest 2:
  ```bash
  $ roll 4d6kh2
  Rolled 4d6kh2 and got 11. Kept [5, 6] and discarded [3, 2].
  ```
- `klc`: `K`eep the `L`owest `c`.
  For example, to roll 4 6-sided dice and keep the lowest 2:
  ```bash
  $ roll 4d6kl2
  Rolled 4d6kl2 and got 5. Kept [2, 3] and discarded [5, 6].
  ```

Of course you can use together an addition with any of the *keep* actions:
```bash
$ roll 4d6+5kh2
Rolled 4d6+5kh2 and got 21. Kept [11, 10] and discarded [8, 7].
```

