# Program to a small protocol

Python often works best when a function asks an object to perform an operation rather than checking its concrete class.
This is **duck typing**: the object's supported operations matter more than its class name.
Duck typing is Python's most common form of polymorphism, one piece of code working with many kinds of object, and it does not require the objects to share a parent class.
A `typing.Protocol` lists the attributes and methods an object should provide for static type checking.
An object can satisfy that protocol without inheriting from it.

```python
from typing import Protocol


class Named(Protocol):
    name: str


def title(item: Named) -> str:
    return item.name.upper()
```

`class Named(Protocol)` declares a protocol; annotated members describe its contract.
For a method declaration, a body of `...` is an ellipsis placeholder.
Annotations do not enforce the protocol at runtime.
`@runtime_checkable` enables limited runtime attribute checks, but it does not validate full type signatures and is unnecessary here.

`io.StringIO` is an in-memory text stream useful for testing.
Its `write(text)` method adds text, and `getvalue()` returns all accumulated text.
Other writers may return `None` from `write`; avoid depending on that return value.

## A read may be only one chunk

A stream-like object may return part of its data on each `read()` call.
Keep reading until it returns an empty string; whitespace inside a nonempty chunk is still data.
A protocol should require only the arguments the consumer actually passes.
If the consumer calls `read()` without a size, an unrelated implementation with just that signature is sufficient.
The consumer does not own a supplied resource unless its contract explicitly says it must close it.
