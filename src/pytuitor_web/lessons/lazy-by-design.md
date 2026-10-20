## Iterables and iterators

Recall that an iterable is something you can loop over, such as a list, and an iterator supplies its items one at a time.
`iter(values)` gets an iterator, which keeps track of the current position.
`next(iterator)` returns the next item or raises `StopIteration` when no items remain.
A `for` loop requests each next item and stops automatically at `StopIteration`.
These agreed operations form the iterator **protocol**, the behavior an object must provide to act as an iterator.

## Comprehensions build complete lists

You have used list comprehensions to transform and filter values.
Here is a short reminder, because generators use the same shape:

```python
numbers = [-2, 0, 3, 2]
squares = [n * n for n in numbers if n > 0]
print(squares)
```

This displays `[9, 4]`.
Python visits each `n`, keeps it if `n > 0`, and puts `n * n` in a new list.
The comprehension's loop variable is local to that comprehension; it does not replace a variable of the same name outside it.

## Produce values only when requested

A **generator** is an iterator that produces values on demand.
A function containing `yield` creates a generator when called:

```python
def doubles(values):
    for value in values:
        yield value * 2


stream = doubles([1, 2])
print(next(stream))
print(next(stream))
```

This prints `2`, then `4`.
`yield` pauses the function and supplies a value; the next request resumes it after that line.
Unlike `return`, it does not finish the function immediately.
Generator expressions use parentheses, as in `(n * 2 for n in values)`.

Generators are consumed once, and their work, including possible errors, happens as values are requested.
They are useful for large or infinite streams because they do not need to build a complete output list.
