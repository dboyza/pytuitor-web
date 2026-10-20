## A compact form of a familiar loop
A list comprehension builds a list in one expression from values you can loop over.
An object you can loop over, such as a list or range, is called an iterable.
`[number * 2 for number in [1, 2, 3]]` produces `[2, 4, 6]`.
The expression before `for` describes the output item.
An optional final `if` filters input items, keeping only those that meet its condition.

```python
lengths = [len(word) for word in ["sun", "a", "moon"] if len(word) > 1]
```

This produces `[3, 4]`.
A regular loop is often clearer when each item needs several decisions or actions such as printing or writing a file.
For integers, `sorted(values)` puts the smallest value first.
Because a set has no reliable display order, sorting a set gives a predictable list of distinct values.
