## Clean up even when something fails

A context manager handles setup and cleanup around a block of code, as with `with open("notes.txt") as file:`.
Classes implement it with `__enter__` and `__exit__`.
This lesson starts from the smaller `contextlib.contextmanager` form, which uses a generator with exactly one `yield`:

```python
from contextlib import contextmanager


@contextmanager
def example():
    print("Starting")
    try:
        yield "ready"
    finally:
        print("Finished")


with example() as status:
    print(status)
```

Code before `yield` runs when entering the block.
The yielded value becomes `status`.
Code in `finally` runs during cleanup, whether the block finishes normally or raises an exception.
A `try`/`finally` ensures cleanup without suppressing that exception.

## Await asynchronous operations

The previous lesson awaited one coroutine at a time and started the event loop with `asyncio.run(...)`.

`asyncio.gather(first, second)` schedules the supplied coroutine objects so they can make progress together.
Awaiting the result waits for their values and returns a list in argument order, even if the second operation finishes first.
The expression `(double(v) for v in values)` creates a generator of coroutine objects.
Putting `*` before it in a function call passes those objects as separate arguments, equivalent to `gather(double(a), double(b))` for two values.
Calling `gather` with no arguments produces an empty result list when awaited.
Async helps when operations can let other work run while waiting for I/O; ordinary blocking calls still prevent the event loop from progressing.
