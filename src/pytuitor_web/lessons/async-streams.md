# Consume an async stream

A **stream** supplies items over time rather than returning a complete collection at once.
The function or object supplying them is the producer.
Some producers must await input/output before their next item is ready.
An **async iterable** is an object usable in `async for`.
Its `__aiter__` method supplies an async iterator, whose `__anext__` method supplies an awaitable for the next item.
You can use `async for` without calling these methods yourself.
An async function containing `yield` is an async generator.
It can both await and yield during iteration.

```python
import asyncio


async def messages():
    for message in ["start", "finish"]:
        await asyncio.sleep(0)
        yield message


async def lengths():
    result = []
    async for message in messages():
        result.append(len(message))
    return result
```

A normal `for` cannot consume an async generator.
`async for` belongs inside an async function and may suspend between iterations.
Returning a final list is appropriate when the contract needs the whole finite result; streaming outputs would instead call for another async generator.
