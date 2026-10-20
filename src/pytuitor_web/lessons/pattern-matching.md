# Match values by their shape

A `match` statement compares one value, the **subject**, against a series of **patterns**.
Python tries each `case` from top to bottom and runs only the first one that fits.
`match` requires Python 3.10 or newer.

```python
def describe(point):
    match point:
        case [0, 0]:
            return "origin"
        case [0, y]:
            return f"on the y axis at {y}"
        case [x, y]:
            return f"at {x}, {y}"
        case _:
            return "not a point"
```

`describe([0, 5])` returns `on the y axis at 5`.

## Kinds of pattern

- A literal such as `0` or `"look"` matches an equal value.
- A bare name such as `y` is a **capture pattern**: it matches anything and stores the value in that name.
- `_` is the **wildcard**: it matches anything without storing it, so `case _:` works as a final default.
- `[x, y]` matches a list or tuple of exactly two items; `["add", *items]` matches `"add"` followed by any number of items, collected in the list `items`.
- `"quit" | "exit"` matches either alternative.
- `{"kind": "move", "to": place}` matches a dictionary containing those keys; extra keys are allowed.

Because a bare name always captures, `case limit:` matches everything; compare with a variable's value using a guard instead.

## Guards and order

A **guard** adds a condition: `case ["go", place] if place in exits:` matches only when the pattern fits and the condition is true.
Otherwise Python continues with the next case.

The first matching case wins, so put specific cases before general ones.
A mapping pattern ignores extra keys, so `{"kind": "move"}` also fits a message that has a `"to"` key; place the case that needs `"to"` first.
If no case fits, the `match` statement does nothing.

Use `match` when the shape of the data decides what happens; for a single simple comparison, `if` is often clearer.
