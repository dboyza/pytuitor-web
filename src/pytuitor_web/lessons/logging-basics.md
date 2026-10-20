# Record what happened with logging

`print()` writes output for the person using a program.
**Logging** records what the program did for the person maintaining it, such as a skipped line or a failed save.
The standard `logging` module lets the application decide where those records go, without changing the code that writes them.

## Loggers and levels

A **logger** is a named object that receives records.
`logging.getLogger("inventory")` returns the logger named `inventory`; the same name always returns the same logger.
Modules usually write `logging.getLogger(__name__)` so each logger is named after its module.

Each record has a level, from least to most serious:

- `logger.debug()` for detailed diagnostic steps.
- `logger.info()` for normal milestones, such as `Loaded 12 items`.
- `logger.warning()` for something unexpected that the program handled.
- `logger.error()` when an operation failed.
- `logger.critical()` when the program cannot continue.

```python
import logging

logger = logging.getLogger("trail")


def read_distance(text):
    try:
        return float(text)
    except ValueError:
        logger.warning("Ignoring distance %r", text)
        return 0.0
```

Pass values as extra arguments rather than building the message with an f-string.
`%r` inserts a value's representation, `%s` its ordinary text, and `%d` a whole number.

## Configure logging once

A **handler** decides where records go, such as the terminal or a file.
`logging.basicConfig(level=logging.INFO)` adds a terminal handler to the root logger, which every named logger passes its records up to.
Call it once, in the program's entry point.
Reusable code should only create records; configuring logging there would override the choices of whichever application uses it.
`logging.info(...)` writes to the root logger directly and hides which module wrote the record, so prefer a named logger.

## Record an exception

Inside an `except` block, `logger.exception("Could not save %s", name)` logs at ERROR level and attaches the traceback, the report of where the error happened.
The program keeps running, and the details reach the log.
