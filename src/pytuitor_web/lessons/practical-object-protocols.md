# Join Python's object conventions

Special methods let user-defined objects participate in ordinary syntax.
`__repr__` supplies a debugging representation, `__len__` supports `len`, `__eq__` supports equality, and `__add__` supports `+`.
An operand is a value an operator works on, such as either value in `left + right`.
For an unsupported operand type, return `NotImplemented` from a two-operand method such as `__add__` or `__eq__`, allowing Python to try the other object's operation or its fallback behavior.
This is a special value, not an exception to raise.

`!r` in an f-string uses a value's representation, including quotes for strings.

```python
class Label:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return f"Label({self.text!r})"

    def __eq__(self, other):
        if not isinstance(other, Label):
            return NotImplemented
        return self.text == other.text
```

A property runs methods when an attribute is read or assigned.
`@property` marks the method that runs when reading `object.celsius`.
`@celsius.setter` marks the method that runs for assignment such as `object.celsius = 20`.

```python
class Temperature:
    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Below absolute zero")
        self._celsius = value
```

The underscore is a convention for internal storage, not access enforcement.
A property supports encapsulation: callers keep writing `object.celsius`, while the class checks every assignment before storing it.
Validate before assigning so rejected updates leave the previous state intact.
