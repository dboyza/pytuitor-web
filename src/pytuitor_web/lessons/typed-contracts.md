# Describe relationships between types

Annotations document expectations; Python does not automatically enforce them.
`str | None` is a union allowing a string or `None`.
After an `if value is None` branch handles `None`, a static checker can treat the corresponding `else` branch as working with a string.
This is called type narrowing.
`list[int]` describes a list containing integers; `Iterable[int]` also permits tuples, generators, and other iterable sources.

A type alias gives a longer annotation a reusable name: `Row = tuple[str, int]` lets you annotate `rows: list[Row]`.
It describes the same underlying types rather than creating a new runtime class.

A type variable connects input and output types without forcing one concrete type.
`T = TypeVar("T")` creates a type variable named `T`.
Using `T` for both the input elements and result tells the checker that their types are related.
This Python 3.11-compatible example preserves the caller's element type:

```python
from typing import TypeVar

T = TypeVar("T")


def repeat(value: T, count: int) -> list[T]:
    return [value for _ in range(count)]
```

`TypeVar` helps a type checker follow those relationships; it does not convert values while the program runs.
For a reusable container, `class Box(Generic[T]):` uses `Generic` from `typing`, and `Box[int]` describes a box for integers.
Use a type variable when types must relate; use a union when a value has several permitted forms.
