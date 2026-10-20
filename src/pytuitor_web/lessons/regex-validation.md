## Describe a text shape
A regular expression, or regex, describes a pattern in text.
Python includes the `re` module; `import re` makes its functions available as `re.function_name(...)`.
A raw string starts with `r` before the opening quote, as in `r"[a-z]+"`.
It keeps backslashes unchanged so the regex code, rather than Python's ordinary string escape rules, can interpret them.
ASCII is the basic character set that includes English letters `A` through `Z`, `a` through `z`, and digits `0` through `9`.
`[a-z]` matches one lowercase ASCII letter, `+` repeats the preceding pattern one or more times, and `{2}` repeats it exactly twice.
A literal hyphen outside square brackets matches a hyphen.

```python
import re

pattern = r"[a-z]+:[0-9]{2}"
print(re.fullmatch(pattern, "room:42") is not None)  # True
print(re.fullmatch(pattern, "room:420") is not None)  # False
```

A match function returns an object describing the matched text when successful and `None` otherwise.
`is not None` turns that result into a Boolean.
`fullmatch` checks the whole string, while `search` finds a matching portion anywhere inside it.
Prefer ordinary string methods for simple operations; use regex when a text shape combines several rules.
