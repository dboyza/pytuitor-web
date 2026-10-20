## Each item has a position
A list keeps its items in order.
An **index** is an item's position, counting from zero.
For `colors = ["red", "blue", "green"]`, `colors[0]` is `"red"` and `colors[2]` is `"green"`.
`colors[-1]` gets the last item.
`len(colors)` returns the number of items, which is `3` here.
An index outside the list raises `IndexError`, an error meaning that the requested position does not exist.
An empty list has no first or last item.

A **slice** takes a portion of a list.
`colors[:2]` gives the first two items; `colors[1:]` gives everything after the first.
Slicing an empty list is allowed and gives another empty list.

```python
colors = input("Colors: ").split()
if len(colors) == 0:
    message = "No colors"
else:
    message = colors[-1]
print(message)
```
