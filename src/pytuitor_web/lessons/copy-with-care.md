## File operations need deliberate behavior
Before automation writes files, decide what happens if a destination already exists.
The `"w"` mode replaces a file.
The `"x"` mode creates a new file only if that name is unused and raises `FileExistsError` otherwise.
This is called exclusive creation.
A prior existence check alone has a gap: another program could create the file before the write starts.
Exclusive creation enforces the rule at the write itself.

Binary mode adds `b`, such as `"rb"` and `"xb"`.
It reads and writes raw bytes, the units used to store file data, without interpreting them as text.
Use it when copying a file exactly.
`shutil.copyfileobj(source_handle, destination_handle)` copies bytes between open files.

```python
import shutil

with open("source.dat", "rb") as source:
    with open("new.dat", "xb") as destination:
        shutil.copyfileobj(source, destination)
```
