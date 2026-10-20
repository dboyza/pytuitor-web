## Keep a fixed group together

A **tuple** is an ordered collection whose items cannot be replaced, added, or removed after creation.
Write a pair with parentheses and a comma, such as `point = (3, 8)`.
The comma makes it a tuple; a one-item tuple needs a trailing comma, as in `(3,)`.
`tuple([3, 8])` converts a list into a tuple.
Tuples support indexing and `len()` just like lists.

**Unpacking** assigns the items of a collection to separate names in order:

```python
point = (3, 8)
x, y = point
print(x)
print(y)
```

This prints `3` and then `8`.
The number of names must match the number of items; otherwise Python raises `ValueError`.
Unpacking also works with lists and with the pairs produced by loop helpers later in this section.

## Keep unique values in a set

A **set** holds distinct values: each value appears once.
Its display order and the order in which a loop visits its items are not guaranteed.
Create one from a list with `set(...)`.
Repeated values appear only once.
An empty set is `set()`, not `{}`.

```python
colors = set(["blue", "gold", "blue"])
print(len(colors))
print("gold" in colors)
print("red" not in colors)
```

This prints `2`, `True`, and `True`.
The **membership** operator `in` asks whether a value is present; `not in` asks whether it is absent.
These operators also work with lists and tuples.
Sets do not support indexing, because there is no first or last position.
