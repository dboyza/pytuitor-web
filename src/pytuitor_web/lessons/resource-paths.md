# Read data with explicit paths

`pathlib.Path` represents a filesystem path and provides methods for reading and writing files.
Accepting a path argument makes code usable from different working directories and easy to test with temporary files.
Specify an encoding for text files so behavior does not depend on local defaults.

```python
from pathlib import Path
import json

path = Path("example.json")
text = path.read_text(encoding="utf-8")
value = json.loads(text)
```

JSON objects become dictionaries, arrays become lists, and null becomes None.
Parsing successfully does not mean the data has the shape your application expects.
`isinstance(value, dict)` tests whether the parsed value is a dictionary.
Malformed JSON, meaning text that breaks JSON syntax rules, raises `json.JSONDecodeError`, a subclass of `ValueError`.
A missing file raises `FileNotFoundError`; catching that specific exception leaves other errors visible.
Catch only exceptions your application can recover from; a permissions error is different from an optional file being absent.
For data delivered inside an installed package, `importlib.resources.files(package)` locates that package's resources, such as bundled text files.
This avoids assuming that the user is running from the source-code directory.
The exercise below instead receives an explicit file path.
