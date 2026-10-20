## Find values, then replace matching text
Parentheses in a regex create a **capture group**, which saves one part of the matched text for you to use.
`re.findall` returns matches in their original order; with one capture group it returns that group's strings.
`re.sub(pattern, replacement, text)` returns a new string with every matching part replaced.

```python
import re

message = "{item:tea} and {item:rice}"
pattern = r"\{item:([a-z]+)\}"
names = re.findall(pattern, message)
print(names)  # ['tea', 'rice']
mask = "{item:sold}"
updated = re.sub(pattern, mask, message)
print(updated)
```

The parentheses capture a name while the surrounding pattern matches the complete marker.
Some characters have special meanings in a regex.
For example, `[` starts a character class, a set of allowed characters such as `[a-z]`.
To match an actual opening bracket instead, write `\[`.
Likewise, `\]`, `\{`, and `\}` match literal brackets or braces.
Backslashes inside raw strings reach the regex code unchanged.
Use the `json` and `csv` modules to read those file formats; their parsing rules handle details a small regex would miss.
