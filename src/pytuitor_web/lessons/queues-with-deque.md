## First in, first out
A queue serves work in arrival order, also called first in, first out or FIFO.
A stack serves the newest item first, also called last in, first out or LIFO.
A deque, pronounced "deck," is a double-ended queue: you can add or remove items at either end.
Python provides it as `collections.deque`.
A list can act as a queue, but removing its first item shifts all later items; `deque.popleft()` avoids that work.

```python
from collections import deque

jobs = deque(["wash", "dry"])
jobs.append("fold")
print(jobs.popleft())  # wash
print(list(jobs))  # ['dry', 'fold']
```

`append` adds one item on the right, `extend` adds each item from a collection on the right, and `popleft` removes and returns the leftmost item.
`pop` removes the rightmost item instead.
An empty deque is false in a condition; check it before removing anything.
For example, `if jobs:` runs its block only while the queue has items.
Removing from an empty deque raises `IndexError`.
