# Control attribute access

A descriptor is an object whose class defines `__get__`, `__set__`, or `__delete__`.
When assigned to an attribute on another class, a descriptor can control what happens when code reads or writes that attribute.
The class containing that attribute is the **owner class**; its objects are the owner instances.
A property is a familiar descriptor; custom descriptors let multiple classes reuse a rule.

`__set_name__(self, owner, name)` is called when the owner class is created, supplying the attribute's declared name.
`__get__(self, instance, owner=None)` handles reads; instance is None when the attribute is read through the class.
`__set__(self, instance, value)` handles writes.
A descriptor that also defines `__set__` or `__delete__` is called a **data descriptor**.
Python uses its methods before checking an ordinary instance attribute with the same name.
A descriptor defining only `__get__` can instead be overridden by an ordinary attribute on that instance.

```python
class Label:
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return "ready"


class Job:
    label = Label()
```

`Job().label` returns a string while `Job.label` returns the descriptor.
The descriptor itself is shared, so per-instance state belongs on the owner instance.
`getattr(obj, name, default)` reads the attribute named by a string, returning `default` when it is absent.
`setattr(obj, name, value)` writes an attribute whose name is supplied as a string.
For example, `setattr(job, "_label", "new")` stores a separate attribute from `job.label`.
A name beginning with one underscore marks an implementation detail by convention; Python does not make it inaccessible.
In `__set_name__`, save a name such as `"_" + name` on the descriptor, then use that name to read and write each owner instance's own value.

## Before controlling attribute access

Review Your first class, Objects that fit Python, and Factories and abstract interfaces before this chapter if instances, properties, or inheritance are unfamiliar.
Ordinary instance attributes live in `instance.__dict__`; a class attribute can instead hold a shared object that manages access.
`getattr(object, name, default)` reads a named attribute with a fallback, and `setattr(object, name, value)` assigns it.
A descriptor must distinguish the shared manager from each instance's stored value.
Class access has no instance, so returning the descriptor itself lets callers inspect the manager without reading an instance value.
