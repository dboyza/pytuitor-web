# Inject effects for reliable tests

Input/output, often shortened to **I/O**, includes reading files, displaying output, and communicating over a network.
A function that controls timing or I/O is easier to test when the operations it relies on are passed as arguments.
This is **dependency injection**.
You can pass a real operation in production and a small fake in tests.
A **mock** is a test object that records how it was called and can supply chosen results or errors.

```python
from unittest.mock import Mock

operation = Mock(side_effect=[ValueError("busy"), 42])
try:
    operation()
except ValueError:
    result = operation()
assert result == 42
assert operation.call_count == 2
```

`side_effect` can provide a sequence of return values and raised exceptions.
`Mock()` without a side effect records calls too.
Inside an exception handler, a bare `raise` re-raises the current exception, keeping the traceback that records where the error passed through the code.
Catch the specific exception that your recovery policy understands; a broad `except Exception` can hide programming errors.
