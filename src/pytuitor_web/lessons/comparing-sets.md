## Compare groups of values

Sets hold unique values and support questions about whole groups.
The operators below create new sets without changing their inputs.

```python
morning = set(["Mira", "Sol"])
evening = set(["Sol", "Bo"])
print(morning & evening)
print(morning - evening)
```

`&` is intersection: the values in both groups, here `Sol`.
`-` is difference: values in the left group that are absent from the right, here `Mira`.
Swapping the left and right sets changes which group you subtract from.
`|` is union, containing everyone from either group.
`^` is symmetric difference, containing only people in exactly one group.

`morning <= evening` asks whether every morning value is also in evening.
A **subset** contains only values that are also in the other set.
Equal sets count as subsets of each other.
`<` means a proper subset: equality is excluded.
An empty set is a subset of every set.
For predictable display, `sorted(values)` returns a new sorted list; a set itself has no guaranteed display order.
