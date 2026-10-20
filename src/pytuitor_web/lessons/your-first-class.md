## Objects keep data and related operations together
A class describes how to create a kind of object.
Each object made from the class is an instance with its own data.
The data an object keeps is its state, and the operations it provides are its behavior.

```python
class Counter:
    def __init__(self, start=0):
        self.value = start

    def increment(self):
        self.value = self.value + 1


counter = Counter(4)
counter.increment()
print(counter.value)
```

`__init__` sets up a new instance.
Python calls it when you create an object with `Counter(4)`, passing `4` as `start`.
`self` refers to the instance receiving a method call; Python supplies it automatically when you call `counter.increment()`.
Attributes such as `self.value` keep data on that object between method calls.
A method is a function defined inside a class.
