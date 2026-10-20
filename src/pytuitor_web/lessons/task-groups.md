# Give tasks a shared lifetime

Awaiting one operation at a time is sequential.
A task schedules a coroutine so it can make progress alongside other tasks when they yield control.
Python 3.11 introduced `asyncio.TaskGroup` to give related tasks a shared lifetime.

```python
import asyncio


async def pair():
    async with asyncio.TaskGroup() as group:
        first = group.create_task(asyncio.sleep(0, result="left"))
        second = group.create_task(asyncio.sleep(0, result="right"))
    return [first.result(), second.result()]
```

`async with` is the form of `with` whose setup or cleanup may need to wait using async operations.
Here, exiting the block waits for every task in the group.
After a successful exit, `task.result()` returns that task's completed value.
An **exception group** is an exception containing multiple errors from related operations.
If a task fails with an ordinary exception, the group cancels remaining tasks, waits for their cleanup, and raises an `ExceptionGroup` containing failures.
`try` with `except* ValueError` can handle matching parts of an exception group; do not combine ordinary `except` and `except*` clauses in the same try statement.
**Cancellation** requests that a task stop; Python raises `asyncio.CancelledError` inside it at an opportunity to stop.
Use `finally` for cleanup and normally allow that exception to reach the caller.
