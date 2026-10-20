# Expressions with intent

This chapter builds on variables, conditions, loops, and functions to explore Python's rules and conventions.
Python uses indentation to group statements and a colon to introduce a block.
Use four spaces for each indentation level.
There are no braces around a function body or an `if` branch.

```python
def greeting(person):
    if person is None:
        return "Hello, guest"
    return "Hello, " + person
```

`def` defines a function, parentheses declare its parameters, and `return` supplies its result to the caller.
A function returns `None` if it reaches the end without a return statement.
Strings use single or double quotes; `None` represents the absence of a value.
Python has one `None` object, so use `is None` to check for it.
Use `==` when comparing ordinary values.

`text.strip()` returns a string without surrounding whitespace.
Strings are immutable: methods produce a new string rather than changing the original.
An empty string is false in a condition, while every nonempty string is true, including `"0"` and `"False"`.
A value is **truthy** when Python treats it as true in a condition and **falsy** when Python treats it as false.
`a or b` evaluates to `a` when `a` is truthy; otherwise it evaluates to `b`.
It does not necessarily return a Boolean.
