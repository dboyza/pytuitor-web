## Read a measurement with a fractional part

In the previous lesson, ordinary `/` division produced a `float`: a number that can have a fractional part, such as `3.5`.
You can also read a float directly from input.
`float()` converts a numeric string, so `float("3.5")` gives `3.5`.
Unlike `int()`, it accepts a decimal point in the input.
Use ordinary `/` division when the fractional part matters.

```python
seconds = float(input("Seconds: "))
minutes = seconds / 60
print(minutes)
```

Typing `90` gives `1.5` minutes.
Typing `30.6` gives `0.51` minutes.
For this lesson, inputs are valid nonnegative measurements, so you do not need to handle invalid text.

## Choose how the result looks

You already used f-strings to put a variable's value into a message.
The braces can hold any expression, not just a variable name, such as `{minutes * 60}`.
Inside the braces, you can also add a **format specifier** after a colon to control how the value looks in text.
The specifier `:.2f` displays a number rounded to two digits after the decimal point.
It adds zeros at the end when needed to show two decimal places.

```python
liters = 2.5
print(f"Water: {liters:.2f} L")
```

This prints `Water: 2.50 L`.
Formatting creates display text; it does not change the number stored in `liters`.
Keep the calculated value in a variable and format it when printing.

Computers store floats using binary (base-two) numbers.
Many decimal fractions cannot be stored exactly this way, so Python stores a nearby value.
For example, `0.1 + 0.2` may display as `0.30000000000000004`.
Formatting helps present a measurement, but does not make the underlying arithmetic exact.
For money, use whole-number cents when exact cent arithmetic is needed.

## Practice in the workspace

Use the active exercise panel beside the editor for the current task requirements and examples.
Use Run to try both fractional input and values that should display trailing zeroes.
Use Check to compare the stored number separately from its formatted text.
