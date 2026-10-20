## Compare two values

A **condition** is an expression used to decide whether some code should run.
The comparisons in this lesson produce either `True` or `False`.
These two values are called booleans, or `bool` in Python.

```python
print(3 > 2)
print(3 == 2)
```

This displays `True`, then `False`.
`>` means greater than, `<` means less than, and `==` asks whether two values are equal.
`>=` and `<=` include equality, while `!=` means not equal.
Remember: `=` assigns a value; `==` compares values.

## Choose which instructions to run

Use `if` to run instructions only when a condition is true.
Use `elif`, short for "else if", to test another condition when the earlier one was false.
Use `else` for everything not handled by the earlier conditions.

```python
weather = "rain"

if weather == "sun":
    print("Bring sunglasses")
elif weather == "rain":
    print("Bring an umbrella")
else:
    print("Bring a jacket")
```

The first comparison is false, so Python tries the `elif` comparison.
That one is true, so it displays `Bring an umbrella`.
A **branch** is one of the groups of instructions the program can choose.
Only one branch in this chain runs; the `else` is skipped.

Each `if`, `elif`, and `else` line ends with a colon, `:`.
The instructions belonging to that branch begin four spaces farther to the right.
This is called **indentation**, and it tells Python which instructions belong together.
The editor inserts spaces when you press Tab.

## Combine conditions

The **Boolean operators** `and`, `or`, and `not` combine conditions.
`a and b` is true only when both conditions are true.
`a or b` is true when at least one condition is true.
`not a` reverses a condition, so `not True` is `False`.

```python
age = 15
has_ticket = True

if age >= 12 and has_ticket:
    print("Board the train")
```

Both comparisons are true, so this displays `Board the train`.

## Practice in the workspace

Use the active exercise panel beside the editor for the current task requirements and cases.
Run the program with an answer from each branch and with an answer that matches no named case.
Check includes boundary cases so you can see whether each comparison includes or excludes equality.
