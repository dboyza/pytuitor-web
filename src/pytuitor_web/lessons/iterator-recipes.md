# Assemble iterator recipes

`itertools` contains small tools for combining streams.
`chain.from_iterable(groups)` yields each group's items in order as they are requested.
This flattens one level: `[["a"], ["b", "c"]]` supplies `"a"`, `"b"`, then `"c"`.
`islice(source, count)` requests at most that many items without exhausting the source.
Together they support previews even when a group is infinite.

```python
from itertools import chain, islice, zip_longest, product

preview = list(islice(chain.from_iterable([["a"], ["b", "c"]]), 2))
```

Ordinary `zip` stops at the shortest input.
`zip_longest(left, right, fillvalue=None)` continues to the longest and pads missing values.
`product(left, right)` produces every pair, with the left item changing slowest.
Unlike `chain`, `product` stores the items from each input before producing pairs, so both inputs must end.

```python
rows = list(zip_longest(["name", "age"], ["Lin"], fillvalue=None))
outfits = list(product(["blue", "green"], ["small", "large"]))
```
