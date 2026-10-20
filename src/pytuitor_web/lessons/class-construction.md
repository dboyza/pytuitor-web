# Separate instances, classes, and helpers

Recall from Inheritance and polymorphism that `class Child(Parent):` creates a subclass, which inherits its parent's methods unless it overrides them.
Creating an instance means calling a class to make an object, as in `Coordinate(2, 3)`.
An ordinary method receives `self`, the instance.
A `@classmethod` receives `cls`, the class used for the call, making it useful for alternate constructors: named methods that create instances.
A `@staticmethod` receives neither automatically; use it for a related helper that does not need instance or class state.

```python
class Coordinate:
    def __init__(self, x, y):
        self.x, self.y = x, y

    @classmethod
    def from_pair(cls, pair):
        return cls(*pair)

    @staticmethod
    def is_pair(value):
        return len(value) == 2
```

`cls(*pair)` unpacks the two values in `pair` into positional arguments and calls the class stored in `cls`.
Using `cls` rather than a fixed class name lets an inherited constructor create the subclass that was called.

Abstraction, showing callers what an object does while leaving how to each class, earlier used `NotImplementedError` for an abstract method.
That error appears only when someone calls the missing method.
An **abstract base class** declares methods subclasses must implement before instances can be created, so the mistake appears as soon as an incomplete class is used.
Inherit from `abc.ABC` and mark required methods with `@abstractmethod`.
This provides explicit inheritance-based interfaces; the next lesson contrasts structural protocols.

```python
from abc import ABC, abstractmethod


class Writer(ABC):
    @abstractmethod
    def write(self, text):
        pass
```

## Alternate constructors can validate configuration

A class factory can convert text into the configuration stored by an instance.
For example, `int("101", 2)` interprets the text as a base-two integer and returns `5`, while `int("ff", 16)` returns `255`.
The optional second argument is the numeric base.
A decoder can validate a base once during construction and reuse it for several conversions.
Keep the static validity predicate separate from conversion, so callers can also check already-converted values.
