import asyncio

import pytest

from pytuitor_web.curriculum import LESSONS
from pytuitor_web.runner import ConsoleSession, execute


async def test_waiting_for_user_does_not_consume_execution_timeout():
    ready = asyncio.Event()
    output = []
    session = ConsoleSession(output.append, lambda waiting: ready.set() if waiting else None)
    task = asyncio.create_task(
        execute(LESSONS[0], 'print(input("Answer: "))', check=False, console=session, timeout=2)
    )
    try:
        await asyncio.wait_for(ready.wait(), 10)
        await asyncio.sleep(2.2)
        assert not task.done()
        assert "Answer:" in "".join(output)
        assert session.submit("Ada")
        result = await asyncio.wait_for(task, 5)
        assert not result.error
        assert "Ada" in "".join(output)
    finally:
        if not task.done():
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task


async def test_cancellation_while_waiting_cleans_up_the_process():
    ready = asyncio.Event()
    session = ConsoleSession(lambda text: None, lambda waiting: ready.set() if waiting else None)
    task = asyncio.create_task(execute(LESSONS[0], 'input("Wait: ")', check=False, console=session))
    await asyncio.wait_for(ready.wait(), 10)
    process = session.process
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert process.returncode is not None
    assert process.stdin.is_closing()
    assert session.process is None
    assert not session.waiting
