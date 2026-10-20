# Define the context-manager methods

Like the iterator protocol, the context-manager protocol is a set of methods Python calls for you.
It uses the two methods below.
`with manager as value:` calls `manager.__enter__()` and assigns its result to `value`.
When the body finishes, Python calls `__exit__(exc_type, exc_value, traceback)`.
All three arguments are `None` for a normal exit.
On failure they hold the exception's class, the exception object, and a traceback recording where the error passed through the code.
Returning a truthy value suppresses the exception, so the caller does not receive it.
Return `False` or `None` to let the exception propagate, meaning continue back to the caller.
Cleanup normally should preserve failures.

As a reminder, a class defines a new kind of object, and calling the class constructs an instance.
Python then calls `__init__` with that instance as `self` and the supplied constructor arguments.
Instance methods also receive `self` automatically, so `self.label` stores a value on this particular object for later methods to use.

```python
class Announce:
    def __init__(self, label):
        self.label = label

    def __enter__(self):
        print("start", self.label)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("finish", self.label)
        return False


with Announce("report") as announcement:
    print(announcement.label)
```

Use suppression only for a narrow, deliberate contract.
`issubclass(error_type, ValueError)` includes subclasses; guard against `None` first.
If `__enter__` raises, Python does not call `__exit__` on that manager.
