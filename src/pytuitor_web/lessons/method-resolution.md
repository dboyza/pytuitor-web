# Understand method lookup with multiple inheritance

The **method resolution order (MRO)** is the sequence of classes Python searches to find an attribute or method.
`Class.__mro__` contains that sequence as a tuple.
Recall that inheritance creates a subclass from a parent class.
**Multiple inheritance** means a class has more than one parent, written as `class Combined(First, Second):`.
It includes each class once in an order compatible with the declared bases.
`super()` continues lookup after the current class in the actual instance's MRO.
It does not simply mean calling a fixed parent.

```python
class Base:
    def describe(self):
        return "base"


class Tagged(Base):
    def describe(self):
        return "tag:" + super().describe()
```

For methods to cooperate, each must accept the arguments passed by the previous method and call `super()` once when more work should follow.
For example, `return ["tag"] + super().steps()` puts one list item before the list returned by the next method.
Calling a particular base directly can skip siblings or execute a shared ancestor twice.
**Composition** means putting another object in an attribute and using that object's methods, instead of inheriting from its class.
It can be easier to follow than many interconnected parent classes.

## Cooperate during initialization

The same MRO rules apply to `__init__`.
A cooperating constructor consumes its own keyword arguments and passes the remainder to the next constructor.

```python
class Tagged:
    def __init__(self, *, tag, **kwargs):
        super().__init__(**kwargs)
        self.tag = tag
```

The bare `*` makes `tag` keyword-only, and `**kwargs` gathers remaining named arguments.
`super().__init__(**kwargs)` forwards them rather than discarding them.
At the end of the chain, `object.__init__` accepts no extra arguments, exposing misspelled or unsupported options as `TypeError`.
Work before `super()` happens on the way down the chain; work after it happens as calls return in reverse order.
Create mutable instance state inside initialization so separate instances do not share it.
