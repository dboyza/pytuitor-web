# Functions are values

A callable is an object you can call with parentheses, including a function.
Pass a function without parentheses when another function should call it later.
`sorted(items, key=function)` calls the key function for each item and sorts by those keys, returning a new list.
Sorting is stable: items with equal keys retain their original order.

`lambda name: expression` creates a small function without a declared name that returns the expression.
Use `def` when a function needs several statements or a descriptive name.

```python
names = ["Ada", "Christopher", "Lin"]
by_length = sorted(names, key=len)
by_last_letter = sorted(names, key=lambda name: name[-1])
```

A **closure** is a function that uses variables from the function where it was defined, retaining access after that outer call returns.
`functools.partial` is another way to make a callable with arguments already supplied.

```python
from functools import partial


def surround(text, left, right):
    return left + text + right


quote = partial(surround, left='"', right='"')
print(quote("hello"))
```
