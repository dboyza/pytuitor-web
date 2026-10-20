## Loop over keys, values, or both

A dictionary stores pairs: each key with its value.
Three methods choose what a loop receives:

- `.keys()` gives each key.
- `.values()` gives each value.
- `.items()` gives each key and value together, as a tuple.

A loop directly over a dictionary, as in `for food in prices:`, visits the keys.
Loops follow the order in which keys were first added.

## Unpack each pair

Recall that a tuple can be unpacked into separate variables.
`.items()` supplies one tuple per entry, so the loop can unpack the key and value directly:

```python
prices = {"soup": 4, "bread": 3}
for food, price in prices.items():
    print(f"{food} costs {price}")
```

This prints `soup costs 4`, then `bread costs 3`.

Writing `for food, price in prices:` is a common mistake.
That loop receives only keys, so Python tries to split each key string into two variables and raises `ValueError` with a message such as `too many values to unpack`.

## Summarize the values

`.values()` works with `sum()`, `max()`, and `min()`:

```python
prices = {"soup": 4, "bread": 3, "tea": 2}
best = max(prices.values())
favorites = []
for food, price in prices.items():
    if price == best:
        favorites.append(food)
print(sum(prices.values()), best, favorites)
```

This prints `9 4 ['soup']`.
To find which keys have the largest value, find the value first, then keep every key whose value matches.

`max(prices)` would compare the keys instead and return `"tea"`, the last name alphabetically.
Say which part of the dictionary you mean.
