# Await cooperative work

Asynchronous code can pause while waiting, allowing other work to make progress.
A **coroutine function**, written with `async def`, is a function that can use `await` to pause and resume.
Calling a coroutine function creates a coroutine object; its body runs when that object is awaited or scheduled.

An **event loop** coordinates this work, running ready operations and waiting when none are ready.
`asyncio.run(coroutine)` creates an event loop, runs the coroutine to completion, and closes the loop.
Use it once at a normal script boundary, not inside a running event loop.

```python
import asyncio


async def greet(person):
    await asyncio.sleep(0)
    return "Hello, " + person


# A script can print(asyncio.run(greet("Nora"))).
```


An **awaitable** is an object accepted by `await`, such as a coroutine object.
`await operation()` waits for that operation to finish and gives its result to the surrounding expression.
While an operation is waiting, the event loop can run other scheduled work.
Awaiting an already completed operation may not give other work a turn.
`asyncio.sleep(0)` explicitly lets other ready tasks take a turn.

This is **concurrency**: multiple operations make progress during the same period.
It is cooperative because each running operation must reach a point that lets others run.
A long calculation or `time.sleep` blocks the event loop, preventing other tasks from running on it.

**Parallelism** means executing work at the same instant, for example on multiple processor cores; async alone does not provide that.

## Before entering async work

You should be comfortable with functions, exceptions, and ordinary iteration before this chapter.
Review Writing functions, Handling invalid input, and Numbering and pairing items if returning values or propagating an exception is unfamiliar.
Calling an `async def` function creates a coroutine object; it does not immediately return the eventual result.
`asyncio.run(...)` owns an event loop for a standalone program, while `await` is used inside an already-running coroutine.
Concurrency means overlapping progress at suspension points; it does not imply simultaneous CPU execution.
