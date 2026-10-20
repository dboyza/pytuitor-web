## Define your own function

You have already called built-in functions such as `print()` and `input()`.
A **function** groups instructions under a name so you can reuse them.
Use `def` to define one:

```python
def double(number):
    return number * 2


answer = double(4)
print(answer)
```

`double` is the function's name.
`number` is a **parameter**, a variable that receives a value when the function is called.
The value `4` in `double(4)` is the argument, just like the values you have passed to `print()`.
The indented line is the function's body.

Defining the function does not run its body.
Calling `double(4)` runs the body with `number` set to `4`.
`return` ends the function and sends `8` back to the caller, which stores it in `answer`.

## Return and print do different jobs

`return` gives the caller a value to use.
`print()` displays something in the console.
A function that finishes without `return` gives back `None`, the "no result" value you saw returned by `sort()`.

```python
def double(number):
    print(number * 2)


answer = double(4)
print(answer)
```

This displays `8`, then `None`.
Printing `8` inside the function did not return it to `answer`.

## Follow an error to its cause

A **traceback** shows the function calls that led to an error.
Read the error type and message at the bottom, then find the last line in your code that it points to.
For example, this function uses two different spellings for its parameter:

```python
def add_bonus(points):
    return point + 5


print(add_bonus(10))
```

The final message is `NameError: name 'point' is not defined`.
The traceback points to `return point + 5` inside the function and also shows the call that reached it.
The parameter is named `points`, so change `point` to `points` and run again.
The output should now be `15`.

Even with that spelling fixed, `add_bonus("10")` fails with a `TypeError` because its argument is a string.
The function tries to add that string to the integer `5`.
Read both the operation and the values involved before choosing a fix: this function expects a number, so call `add_bonus(10)`.
If the value comes from `input()`, convert the input text with `int()` first.
Run again after each correction and compare the result with what you expected.
