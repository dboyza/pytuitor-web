# Keep imports predictable

A Python file is a module.
Its **namespace** is the collection of names it defines, such as function and variable names.
`from tools import normalize` imports a named object from `tools.py`.
The module body executes on its first import in a process, and later imports normally reuse its entry in `sys.modules`.
A module's **API**, or application programming interface, is the set of functions and other objects that callers use.
Importing a reusable module should usually define these objects without printing, asking for input, or starting work.

```python
# helpers.py
def loud(text):
    return text.upper()


if __name__ == "__main__":
    print(loud("demo"))
```

The guard runs the demonstration when that file is executed as the main program, but not when imported as helpers.
A local file named `json.py` or `typing.py` may be imported instead of the standard-library module with that name.
This is called **shadowing**; choose a different name to avoid it.
Packages group modules under directories, conventionally with an `__init__.py`; imports inside a package may be absolute or explicitly relative, such as `from .helpers import loud`.
