# Preserve the reason for failure

Custom exceptions give callers a meaningful category to catch.
Recall that a subclass inherits behavior from an existing class.
`class ConfigurationError(ValueError):` defines a new error class that is also a `ValueError`, so `except ValueError` catches it too.
Use `pass` for an otherwise empty class body when no additional behavior is needed.
`raise NewError(...) from error` stores the original error on the new error's `__cause__` attribute.
This is exception chaining: an error report can show both what failed and the underlying reason.
Catch only errors you can meaningfully handle or translate.

```python
class ConfigurationError(ValueError):
    pass


try:
    timeout = int("soon")
except ValueError as error:
    raise ConfigurationError("Timeout must be an integer") from error
```

`finally` runs when a `try` block exits, including through a return or an exception.
Use it for cleanup; avoid returning from `finally`, which would hide failures.
A following lesson introduces context managers to package this pattern.

```python
handle = open("notes.txt")
try:
    text = handle.read()
finally:
    handle.close()
```
