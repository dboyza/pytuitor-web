# Consume only what you need

An iterable can provide an iterator; an iterator remembers its position.
`iter(values)` obtains an iterator, and `next(iterator)` advances it or raises `StopIteration` when exhausted.
The optional second argument to `next` supplies a default instead of raising.
A generator function uses `yield` and pauses between values, as in the previous lesson.

```python
from itertools import islice

source = iter(range(100))
first_three = list(islice(source, 3))
next_two = list(islice(source, 2))
```

`islice` requests only the selected part of a stream.
Collecting an infinite stream into a list would never finish.
A lazy operation must read only enough input to produce the next requested result.
Once you yield a mutable object, callers may keep it.
Reusing and clearing that same list for the next batch would change the caller's previous result too.

## Keep a sliding history

The `deque` from Queues with deque can also keep a bounded history.
`deque(maxlen=2)` keeps at most two values; appending a third automatically discards the oldest.
For example, after appending `"a"`, `"b"`, and `"c"`, converting the deque to a tuple gives `("b", "c")`.
A **window** overlaps its predecessor, while a batch starts after the previous batch ends.
Converting each completed window to a tuple creates a stable snapshot that later appends cannot change.
