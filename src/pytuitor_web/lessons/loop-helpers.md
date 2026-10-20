## Generate a sequence of numbers

`range()` supplies whole numbers for a loop without requiring a written list.
`range(4)` gives `0`, `1`, `2`, `3`: it starts at zero and stops before `4`.
`range(2, 5)` gives `2`, `3`, `4`.
An optional third argument sets the step, so `range(6, 0, -2)` gives `6`, `4`, `2`.
A range that cannot reach any values in its direction is empty, as in `range(1, 1)`.

```python
for floor in range(2, 5):
    print(floor)
```

This prints `2`, `3`, and `4` on separate lines.
When counting upward one at a time, use one more than the final number as the stopping value.

## Number items while visiting them

`enumerate()` supplies a pair containing a counter and the current item.
It starts counting at zero unless you provide `start=1` or another starting value.
`start=1` is a **keyword argument**: it names the setting whose value you are passing.
Unpack each pair into two loop variables:

```python
for position, task in enumerate(["wash", "dry"], start=1):
    print(f"{position}: {task}")
```

This prints `1: wash` and `2: dry`.
The list remains unchanged.
If the list is empty, the loop does not run.

## Walk through two collections together

`zip()` supplies pairs of corresponding items from two collections.
Its default behavior stops when the shorter collection runs out.
Extra items in the longer collection are ignored.

```python
foods = ["soup", "salad", "bread"]
prices = [4, 6]
for food, price in zip(foods, prices):
    print(f"{food}: {price}")
```

This prints `soup: 4` and `salad: 6`; there is no pair for `bread`.
If either collection is empty, there are no pairs.
When mismatched lengths would be a mistake in a real program, check the lengths first.
In this exercise, ignoring unpaired items is intentional.
