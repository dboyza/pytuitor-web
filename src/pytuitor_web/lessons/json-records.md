## JSON stores familiar data structures
JSON is a text format for exchanging structured data.
JSON uses the name **object** for a collection of named values, like a Python dictionary.
It uses **array** for an ordered collection, like a Python list.
It also supports strings, numbers, Boolean values, and `null`, which represents no value.
Python's `json` module converts between JSON and Python values.
In JSON, `true`, `false`, and `null` become Python's `True`, `False`, and `None`.

```python
import json

text = json.dumps({"city": "Oslo", "days": 2})
record = json.loads(text)
print(record["city"])
```

`dumps` creates a string; `loads` reads a string.
`dump(value, handle)` and `load(handle)` work directly with an open text file.
Invalid JSON raises `json.JSONDecodeError`.
Use UTF-8 when opening the file.
JSON object keys are strings.
