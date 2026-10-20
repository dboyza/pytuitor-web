## An exception reports a failed operation
An **exception** reports an error while a program runs.
**Raising** an exception means reporting that error; **catching** or **handling** it means running code that responds to it.
`int("twelve")` raises `ValueError` because the text is not a valid integer.
A **block** is a group of indented instructions.
A `try` block lets you attempt an operation, and an `except` block handles a particular exception.

```python
def read_count(text):
    try:
        number = int(text)
    except ValueError:
        return 0
    return number
```

If conversion succeeds, Python skips the `except` block.
If it raises `ValueError`, Python runs that block instead.
Catch the specific exception you expect so unrelated programming mistakes remain visible.
Recall that `None` represents the absence of a result.
It is different from the string `"None"` and the number `0`.
`result is None` is the conventional way to test for it.
