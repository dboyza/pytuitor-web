## Repeat while a condition stays true
A `for` loop visits a known collection.
A `while` loop repeats as long as its condition is true.
A variable used in that condition usually needs to change, or the loop may never stop.

```python
remaining = 3
while remaining > 0:
    print(remaining)
    remaining = remaining - 1
```

This prints `3`, `2`, `1`, then stops when `remaining` becomes zero.
`break` immediately stops the loop that contains it.
If loops are nested, it stops only the innermost one.
`while True:` creates a loop that keeps going until something such as `break` stops it.
This is useful when the user decides when they are finished.
