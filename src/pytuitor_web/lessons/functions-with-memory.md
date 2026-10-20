## Defaults are created when a function is defined

Python evaluates a default argument once, when it executes the `def` statement.
The same default object is reused whenever a caller omits that argument.

```python
def collect(item, bucket=[]):
    bucket.append(item)
    return bucket


print(collect(1))
print(collect(2))
```

The second call returns `[1, 2]`, not `[2]`.
Use `None` as the default and create a new list inside the function when `bucket is None`.
Do not use `if not bucket`: an explicitly supplied empty list is false in a condition but should still be reused.

## Functions can wrap other functions

A **decorator** is a function that receives another function and returns its replacement.
Functions are values in Python: you can pass them as arguments, return them, and call them through variables.
A wrapper is a function that calls another function while adding behavior around that call.
In a definition, `*args` collects positional arguments into a tuple and `**kwargs` collects keyword arguments into a dictionary.
In a call, `fn(*args, **kwargs)` passes those collected arguments on to `fn`.
Writing `@announce` above a function definition means replacing that function with `announce(function)`.
The helper decorator `@wraps(fn)` copies descriptive information, called metadata, from `fn` to its wrapper.
That includes `__name__`, the function's name, and `__doc__`, its docstring: an optional string at the start of the function body describing its use.

```python
from functools import wraps


def announce(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print("Calling", fn.__name__)
        return fn(*args, **kwargs)

    return wrapper
```

The wrapper remembers `fn` from the enclosing function, so it is a closure, as in Callable tools and sorting.
A scope is the region where a name is available.
Python looks up names in the current function, then enclosing functions, then the module, and finally its built-in names.

## Cache keys and successful results

A cache remembers a result so repeating the same request can reuse it.
Dictionary keys must be **hashable**, meaning their hash stays stable while they are used as keys.
Integers, strings, and tuples of hashable values can be keys; lists and dictionaries cannot.
Convert keyword pairs to `tuple(sorted(options.items()))` when keyword order should not matter.
A cached `None` or `False` is still a result: use membership to distinguish a missing entry from a falsy stored value.
Assign a result to the cache only after the wrapped call succeeds.
