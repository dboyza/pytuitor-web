## Dictionaries for counting and grouping
The standard-library `collections` module provides dictionaries with useful extra behavior.
`Counter` counts how many times each item appears and treats an unseen key as zero.
`defaultdict` creates a default value when you access a missing key.

```python
from collections import Counter, defaultdict

colors = Counter(["blue", "gold", "blue"])
print(colors["blue"])  # 2
print(colors["green"])  # 0

by_initial = defaultdict(list)
for word in ["tea", "toast", "rice"]:
    by_initial[word[0]].append(word)
print(dict(by_initial))  # {'t': ['tea', 'toast'], 'r': ['rice']}
```

Pass `list`, not `list()`, so `defaultdict` can call it to create a separate empty list for each missing key.
`dict(...)` converts either type to an ordinary dictionary to return to the caller.
Counting and grouping preserve different information: counts keep quantities, while grouped lists keep the original items.
