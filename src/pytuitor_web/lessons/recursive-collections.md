## Lists can contain lists
A nested list is a list containing other lists, such as `["tea", ["bread", "rice"]]`.
The inner list can contain more lists in turn.
`isinstance(value, list)` returns `True` when a value is a list.
This lets a recursive function decide whether to visit children or handle one ordinary item.

```python
def count_words(items):
    count = 0
    for item in items:
        if isinstance(item, list):
            count += count_words(item)
        else:
            count += 1
    return count


print(count_words(["tea", ["bread", ["rice"]]]))  # 3
```

An empty list contributes zero, so it is a base case without a special `if` statement.
Each recursive call receives an inner list, moving deeper into a finite structure until there are no children left.
The nesting structure is sometimes called a tree: each list branches into its items.
