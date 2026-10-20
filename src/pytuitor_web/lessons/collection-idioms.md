# Group without losing order

Lists preserve sequence order; dictionaries associate keys with values.
Dictionary insertion order is part of Python's language contract.
Sets efficiently represent membership and uniqueness but do not promise insertion order.
Choose your container according to the behavior your caller needs.

```python
counts = {}
for word in ["red", "blue", "red"]:
    counts[word] = counts.get(word, 0) + 1

lengths = {word: len(word) for word in counts}
short_words = [word for word in counts if len(word) < 4]
```

The last two expressions are dictionary and list comprehensions.
They work well for a direct transformation or filter; ordinary loops are clearer when an iteration performs several updates.
`mapping.setdefault(key, default)` inserts the default only if the key is absent, then returns the stored value.
`item in collection` tests membership.
`for key, value in pairs` unpacks each two-item pair into two variables.
An **iterable** supplies items to a loop, as lists and tuples do.
An **iterator** supplies items one at a time and remembers how far it has advanced.
A one-pass iterator cannot start over after its items have been read.
A function accepting any iterable therefore cannot assume indexing or a second traversal will work.
