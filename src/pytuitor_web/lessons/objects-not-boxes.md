## Python syntax you will use

A dictionary stores values under keys: `record = {"tags": ["python"]}` creates a dictionary containing a list.
`record["tags"]` accesses the list; `.append("cli")` adds an item to that list.
Use `def` followed by a function name and parameters to define a function.
End that line with a colon and indent its body by four spaces:

```python
def tag_count(record):
    return len(record["tags"])


print(tag_count({"tags": ["python"]}))
```

This prints `1`.
`return` sends a value back to the caller, while `print()` displays a value.
Python needs no braces around the function body or semicolons after instructions.
`from module import function` makes a function from another module available in this file.
A module is a Python file containing reusable code; the standard library comes with Python.

## Assignment does not copy an object

This chapter assumes you can already write variables, conditions, loops, and functions.
If you need an introduction to those ideas, open Foundations in the syllabus; your existing drafts remain saved.

In Python, variables refer to objects.
Assigning `b = a` makes both variables refer to the same object; it does not create a copy.
`==` compares values, while `is` compares object identity.
Use `is None` to test for `None`, and `==` for ordinary value comparisons.

```python
original = [1, 2]
alias = original
alias.append(3)
print(original)
```

The output is `[1, 2, 3]` because `.append()` modifies the shared list.
An object that can be changed in place is **mutable**.
Lists and dictionaries are mutable; strings, integers, and tuples are immutable.
A tuple can still contain a mutable object, such as a list.

## Shallow and deep copies

`.copy()` creates a shallow copy: a new outer container with references to the same contents.

```python
original = {"tags": ["python"]}
copied = original.copy()
copied["tags"].append("cli")
print(original["tags"])
```

This displays `['python', 'cli']` because the nested list is shared.
`from copy import deepcopy` imports a standard-library function that copies nested objects too.
Use it when the new structure must be independent of the original.
