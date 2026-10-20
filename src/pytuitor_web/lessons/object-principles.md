## Four ideas behind classes

Programmers describe class design with four standard terms: encapsulation, abstraction, inheritance, and polymorphism.
You will meet them in documentation, code reviews, and interviews; this lesson defines each one with a single example.

## Encapsulation

**Encapsulation** means keeping an object's data together with the methods allowed to change it, so other code uses those methods instead of editing the data directly.
The methods can then enforce rules:

```python
class Light:
    def __init__(self, name, fuel):
        if fuel < 0:
            raise ValueError("Fuel cannot be negative")
        self.name = name
        self._fuel = fuel

    def hours_left(self):
        return self._fuel

    def describe(self):
        return f"{self.name}: {self.hours_left()} hours left"
```

A leading underscore, as in `_fuel`, means "internal: use this class's methods instead".
Python does not block access to it; the underscore is a convention that readers respect.

## Abstraction

**Abstraction** means letting callers use what an object does without knowing how it does it.
A caller writes `light.hours_left()` without knowing how the hours are calculated, so that calculation can change later without breaking the caller.

A class can also name an operation that more specific classes must provide.
This is an **abstract method**; a simple version raises `NotImplementedError`, an error meaning "a more specific class must provide this".

## Inheritance

**Inheritance** creates a new class from an existing one.
The existing class is the **base class**, or parent; the new class is a **subclass**, or child.
A subclass has every method of its parent.
It can **override** a method by defining one with the same name:

```python
class Candle(Light):
    def hours_left(self):
        return self._fuel // 2
```

`Candle` inherits `__init__()` and `describe()`, and replaces only `hours_left()`, because a candle burns twice as fast.

When a subclass needs extra setup, its `__init__()` should first run the parent's.
`super()` gives access to the parent's methods:

```python
class Lantern(Light):
    def __init__(self, fuel, wicks):
        super().__init__("Lantern", fuel)
        self.wicks = wicks

    def hours_left(self):
        return self._fuel // self.wicks
```

`super().__init__("Lantern", fuel)` stores the name and checks the fuel using `Light`'s rules.
Without it, a `Lantern` has no `name` or `_fuel`, and a later method raises `AttributeError`.

A subclass object also counts as its parent's type: `isinstance(Candle("Candle", 6), Light)` is `True`.

## Polymorphism

**Polymorphism**, meaning "many forms", lets one piece of code work with different kinds of objects, as long as each provides the operation it uses.

```python
lights = [Light("Torch", 5), Candle("Candle", 6), Lantern(8, 2)]
for light in lights:
    print(light.describe())
```

This prints `Torch: 5 hours left`, `Candle: 3 hours left`, and `Lantern: 4 hours left`.
The inherited `describe()` calls `self.hours_left()`, and each object runs its own version.
The loop never checks which class it has, so a new kind of light needs no change to the loop.
