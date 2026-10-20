# Transform, select, accumulate

A **predicate** is a callable used to decide whether an item should be kept, usually by returning `True` or `False`.
A **lazy** operation does work only as results are requested.
An iterator provides those results one at a time and remembers its current position.
`map(function, iterable)` lazily transforms each value.
`filter(predicate, iterable)` lazily keeps values for which a callable returns a truthy result.
They return iterators, so `list(...)` consumes them to produce a list.
A comprehension often expresses the same operation more clearly.

```python
lengths = list(map(len, ["oak", "willow"]))
long_names = list(filter(lambda name: len(name) > 3, ["oak", "willow"]))
```

An accumulator holds the result built so far, like a running total.
A **fold** repeatedly combines that result with the next item.
`functools.reduce(combine, items, initial)` performs a left fold.
Here `combine` is a **callback**, a function passed in for another operation to call.
Its first argument is the current accumulator and its second is the next item.
The explicit initial value also defines the result for empty input.
Prefer `sum`, `min`, `max`, or `any` when one directly expresses your intent.

```python
from functools import reduce

path = reduce(lambda parent, name: parent + "/" + name, ["notes", "today"], "home")
```
