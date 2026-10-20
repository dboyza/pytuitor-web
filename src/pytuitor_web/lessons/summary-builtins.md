## Summarize a whole list at once

You have used built-in functions such as `print()`, `int()`, and `len()`.
Three more answer common questions about a list of numbers:

- `sum(numbers)` adds the items.
- `max(numbers)` returns the largest item.
- `min(numbers)` returns the smallest item.

```python
distances = [4, 9, 2]
print(sum(distances))
print(max(distances))
print(min(distances))
```

This prints `15`, `9`, and `2` on separate lines.
`sum(distances)` replaces a loop that starts a total at zero and adds each item.

## Empty lists need care

`sum([])` returns `0`, because adding no numbers gives zero.
`max([])` and `min([])` raise `ValueError`: an empty list has no largest or smallest item.
Check the length first when a list might be empty:

```python
if len(distances) == 0:
    print("No trips")
else:
    print(max(distances))
```

## Ask whether any or all items are true

`any()` and `all()` take a list of booleans, the `True` and `False` values that comparisons produce.
`any(flags)` returns `True` when at least one item is `True`.
`all(flags)` returns `True` when every item is `True`.

A loop can build the list of booleans, one comparison per item:

```python
ages = [15, 21, 34]
adults = []
for age in ages:
    adults.append(age >= 18)
print(any(adults))
print(all(adults))
```

`adults` is `[False, True, True]`, so this prints `True`, then `False`.

For an empty list, `any([])` is `False` because there is no true item.
`all([])` is `True` because there is no false item to break the rule.
Decide deliberately what an empty list should mean in your program.
