## Keep several values in a list

A **list** holds values in order.
Write square brackets around the values and separate them with commas:

```python
pouches = [2, 5, 1]
```

This list contains three integers.
`[]` is an empty list.
A list can also contain strings, such as `["map", "rope"]`.

## Repeat an instruction with for

A **loop** runs instructions repeatedly.
Each repetition is called an **iteration**.
A `for` loop works through a collection, one item at a time:

```python
for coins in pouches:
    print(coins)
```

On the first repetition, `coins` is `2`; on the next it is `5`; on the last it is `1`.
The program prints those three numbers on separate lines.
Choose any helpful variable name in place of `coins`.
The colon and indentation work just as they do with `if`.

## Build a running total

Start at zero before the loop and add each item:

```python
prices = [3, 4]
total = 0
for price in prices:
    total = total + price
print(total)
```

The total changes from `0` to `3`, then to `7`.
Python calculates the right side before assigning the new total.
`total += price` is a shorter way to write this addition.

## Read a line into numbers

`input()` gives your program one string, even when the user types numbers.
Calling `.split()` turns a space-separated string such as `"2 5 1"` into the list `['2', '5', '1']`.
Loop over those text pieces and call `int()` on each one when you need whole numbers.
For example:

```python
pouches = []
for amount in input("Coins in each pouch: ").split():
    pouches.append(int(amount))
```

A **method** is an operation called through a value with a dot, such as `text.split()`.
`pouches.append(value)` adds one value to the end of the list.
After entering `2 5 1`, `pouches` contains `[2, 5, 1]`.
