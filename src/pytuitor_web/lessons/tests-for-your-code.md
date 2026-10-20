## Tests check the results you expect
You have used Check to compare actual results with expected ones.
You can write expectations for your own programs too.
`assert expression` raises `AssertionError` if the expression is false.
A test suite is a collection of tests.
The standard-library `unittest` module organizes them and reports failures.

```python
import unittest


class AdditionTests(unittest.TestCase):
    def test_two_numbers(self):
        self.assertEqual(2 + 3, 5)
```

A test class inherits from `unittest.TestCase`; the parentheses name the base class whose testing tools it uses.
The test runner, the code that executes the tests, finds methods whose names begin with `test_`.
`self.assertEqual(actual, expected)` reports a failure if values differ.
In an external terminal, `python -m unittest` runs the `unittest` module and looks for test files.
Their names start with `test` and end with `.py`, for example `test_addition.py`.
Here, Check will load and run the test class for you.
