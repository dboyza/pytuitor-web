# Register classes deliberately

A class is itself an object, usually created by `type`.
A metaclass customizes that creation process.
A metaclass can enforce rules while classes are created, such as rejecting duplicate registration names.
For simpler registration, a class decorator or the `__init_subclass__` method covered in this chapter's project may be enough.

```python
class NamedMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        cls.display_name = name.lower()
        return cls


class Report(metaclass=NamedMeta):
    pass
```

`__new__` creates an object; here the object being created is a class.
`mcls` is the metaclass receiving the call, a conventional parameter name like `self`.
`name` is the new class's name.
`namespace` is the dictionary created by executing the class body.
`bases` is a tuple of parent classes.
`super().__new__` delegates creation to the next implementation in the inheritance order.
The example passes every received argument onward, including extra keyword arguments collected by `**kwargs`.
Keep the original namespace dictionary so Python can preserve internal entries needed by methods using `super()`.
The returned `cls` is the new class object; return it after adding or checking attributes.
The metaclass can also be called directly, such as `NamedMeta('Report', (), {})`.
Checking namespace distinguishes an attribute explicitly defined by this class from one inherited from a parent.

## Read class creation in order

A class statement first prepares a namespace containing its directly declared attributes.
A metaclass receives the class name, base classes, and that namespace, then creates the class object.
Checking the namespace distinguishes a new declaration from an inherited attribute.
If class creation updates a registry, validate a duplicate before changing the registry so a refused class cannot replace a working registration.
Prefer a plain dictionary or `__init_subclass__` when they express the same need more directly.
