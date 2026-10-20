# Make call sites readable

Python callers can usually pass arguments by position or by parameter name.
Defaults apply when an argument is omitted.
A bare `*` in a parameter list makes all following parameters keyword-only.
A `/` marks preceding parameters positional-only: callers must supply those arguments without parameter names.
These calling rules form part of a function's public interface, often called its API.

The conditional expression is `value_if_true if condition else value_if_false`.
Ordinary `if` statements are equally appropriate when they are clearer.

```python
def greeting(name, /, salutation="Hello", *, excited=False):
    ending = "!" if excited else "."
    return salutation + ", " + name + ending


greeting("Ravi", salutation="Welcome", excited=True)
```

Defaults are evaluated when `def` executes, a rule explored with mutable objects in the Decorators chapter.

Use `raise ValueError("explanation")` when an argument has an unacceptable value.
Python supports chained comparisons: `0 <= rate <= 1` tests both boundaries.
`round(number, 2)` rounds to two decimal places.
Binary floats cannot exactly represent every decimal fraction; this exercise teaches call contracts, not production money arithmetic.
Financial applications often use `decimal.Decimal` with an explicit rounding policy.
