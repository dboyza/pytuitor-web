## Change a list deliberately

`items.insert(index, value)` inserts before the given position.
`items.append(value)` adds at the end.
`items.remove(value)` deletes the first matching value, raising `ValueError` if none exists.
Check `if value in items:` before removing a value that might be absent.
`items.pop(index)` instead removes and returns the item at an index; without an index it uses the last item.

```python
colors = ["red", "blue", "red"]
colors.remove("red")
colors.insert(0, "gold")
colors.sort()
print(colors)
```

This prints `['blue', 'gold', 'red']`.
`sort()` changes the list and returns `None`, Python's value for no result.
Do not assign that result back to the list.
`sorted(colors)` would return a new sorted list instead.

## Change a dictionary

Assigning `counts[key] = value` inserts or replaces an entry.
`del counts[key]` removes an existing entry and raises `KeyError` for an absent key.
`counts.pop(key, default)` removes and returns the value, or returns the default when absent.
`keys()`, `values()`, and `items()` provide **views**: objects you can loop over to read the dictionary's keys, values, or key/value pairs.
Views reflect later dictionary changes; `list(counts.keys())` copies the current keys into a separate list.
Avoid adding or removing dictionary entries while looping over a view.
