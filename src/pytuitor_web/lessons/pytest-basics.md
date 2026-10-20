# Test with pytest

> Internet use: The exercise and its checks run offline with the copy of pytest included in Pytuitor.
> Installing pytest in your own projects downloads it from the internet.

**pytest** is the most widely used third-party test runner for Python.
It runs the same kind of checks as `unittest`, with less code: plain functions and plain `assert` statements.

## Write a test

pytest **discovers** tests by name: it looks in files named `test_*.py` and runs each function whose name starts with `test_`.
A function named `check_area` never runs.

```python
from sizes import area


def test_area_of_a_square():
    assert area(3, 3) == 9
```

When an assert fails, pytest prints both sides of the comparison, such as `assert 8 == 9`.
In your own projects, run tests from a terminal with `python -m pytest`; in this chapter, Check runs them and shows pytest's report in the console.

## Expect an error

`pytest.raises(ValueError)` passes only if the code inside its `with` block raises that error:

```python
import pytest


def test_rejects_negative_width():
    with pytest.raises(ValueError):
        area(-1, 3)
```

Put only the call that should fail inside the block.
If nothing inside it raises, pytest reports `DID NOT RAISE` and the test fails.

## Run one test with many inputs

`@pytest.mark.parametrize` turns one test into several, one per row of data:

```python
@pytest.mark.parametrize(
    "width, height, expected",
    [(2, 3, 6), (0, 5, 0), (1, 1, 1)],
)
def test_area(width, height, expected):
    assert area(width, height) == expected
```

pytest reports three separate tests, so one failing row does not hide the others.

## Fixtures provide what a test needs

A **fixture** prepares something for a test; the test asks for it by naming it as a parameter.
`tmp_path` gives each test an empty temporary folder.
`monkeypatch` temporarily replaces an attribute, such as a function, and restores it after the test.
`@pytest.fixture` turns your own function into a fixture.

## Tests must be able to fail

A test is useful only if it fails when the code is wrong.
Imagine a broken version of the function and ask whether any test would notice.
Cover boundaries, such as 0 and the largest allowed value, and every error the function promises to raise.
