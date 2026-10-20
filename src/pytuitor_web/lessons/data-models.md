# Model a small value object

As in Your first class, a regular class initializes attributes in `def __init__(self, ...)`, and its methods receive the instance as `self`.
For records, `dataclasses.dataclass` can generate initialization, equality, and readable text for inspecting an object.
A **field** is a named piece of stored data, such as `x` or `y` below.
`@dataclass(...)` applies this behavior to the class written immediately below it, using its annotated fields.

`frozen=True` prevents normal attribute assignment; it does not recursively freeze objects stored in fields.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def shifted(self, dx, dy):
        return Point(self.x + dx, self.y + dy)
```

`Point(2, 4).shifted(1, 0)` constructs a new point.
Value equality compares field values, unlike the identity comparison `is`.
Annotations describe intended types but do not automatically validate values.
A hand-written class with equivalent behavior is also valid.

## Validate related fields

`__post_init__` runs after a dataclass constructor assigns its fields.
It can reject an invalid relationship by raising ValueError, even in a frozen dataclass.
`max(a, b)` selects the larger value, and `min(a, b)` the smaller.
For intervals, a shared endpoint still belongs to both intervals; only a strict gap means there is no overlap.
A method may return a new value or None to represent that absence without mutating its operands.
