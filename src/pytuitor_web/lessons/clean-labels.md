## String methods return changed text
Like `.split()` and `.append()`, string methods are operations called through a value with a dot.
**Whitespace** includes spaces, tabs, and line breaks.
`"  Sunset  ".strip()` removes whitespace from both ends.
`"Sunset".lower()` returns `"sunset"`.
These methods return new strings; they do not change the original string.
You can chain methods because each returned string has its own methods.
`"  Sunset  ".strip().lower()` returns `"sunset"`.

`" ".join(["one", "two"])` joins strings with a space between them.
With no arguments, `.split()` splits on whitespace and ignores repeated whitespace.
Combining split and join can replace any run of whitespace with one separator.

```python
def tidy_title(text):
    words = text.strip().split()
    return " ".join(words)


print(tidy_title("  Night   sky  "))
```

## Title case

`.title()` uppercases the first letter of each word and lowercases the remaining letters.
It starts a new word after punctuation too: `"DON'T stop".title()` gives `"Don'T Stop"`.
It does not clean up whitespace, so use split and join first when spacing matters.
