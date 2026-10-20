# Construct valid, independent values

A dataclass generates initialization and equality from annotated fields.
For mutable defaults, `field(default_factory=list)` calls `list()` for each new instance instead of sharing one list.
Pass the callable `list`, not an already-created `list()`.

`__post_init__` runs after the generated `__init__` method has stored the fields, making it a useful place to clean up and validate their values.
The annotation `list[str]` means a list whose items should be strings.
`dataclasses.replace(instance, field=value)` constructs a new instance and runs initialization again.
It is a shallow operation: unchanged mutable fields are shared unless explicitly copied.

```python
from dataclasses import dataclass, field, replace


@dataclass
class Team:
    title: str
    members: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.title = self.title.strip()


original = Team(" Helpers ", ["Lin"])
copy = replace(original, title="Reviewers", members=original.members.copy())
```
