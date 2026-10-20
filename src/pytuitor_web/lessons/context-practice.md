# Restore temporary state

A context manager performs setup before a `with` block and cleanup afterward.
The `with` statement runs its exit behavior even if the block raises an exception.
A generator decorated with `contextlib.contextmanager` expresses this using one `yield`.

```python
from contextlib import contextmanager


@contextmanager
def marked(events):
    events.append("enter")
    try:
        yield events
    finally:
        events.append("leave")


log = []
with marked(log) as current:
    current.append("work")
```

The value yielded becomes the value after `as`.
When the block ends normally, execution resumes after `yield`.
If it raises, that exception is raised at the suspended `yield`.
A `finally` clause runs in both cases.
Suppressing an exception means handling it without passing it back to the caller.
Do this only when the required behavior explicitly calls for it.
