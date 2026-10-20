## Give fixed choices names
An enumeration, or enum, represents a fixed set of named choices.
It helps avoid misspelled strings spreading through a program.
`from enum import Enum` imports a class supplied by the standard library.
Writing `class Size(Enum):` makes `Size` a subclass of `Enum`.
A subclass inherits behavior from its base class, so `Size` gets the ability to define named choices and look them up by value.
Each choice, such as `Size.SMALL`, is called an enum member.

```python
from enum import Enum


class Size(Enum):
    SMALL = "small"
    LARGE = "large"


choice = Size("small")
print(choice is Size.SMALL)  # True
print(choice.name)  # SMALL
print(choice.value)  # small
```

Use `Size.SMALL` to access the named choice directly.
`Size("small")` looks up that same choice using its stored string value.
`is` checks identity: each member is the same unique enum object every time you access it.
`Size("missing")` raises `ValueError`.
When reading a choice from user input, catch that error where you convert the string to an enum member.
Enums suit a fixed set of choices, while ordinary strings suit open-ended text such as a user's name.
