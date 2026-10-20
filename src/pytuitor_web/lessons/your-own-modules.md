## A Python file can be a module
You have imported standard-library modules such as `json`.
Your own `.py` files can be imported too.
A module name is usually the filename without `.py`.

```python
# In greetings.py:
def hello(person):
    return f"Hello, {person}"
```

```python
# In lesson.py, in the same folder:
from greetings import hello

print(hello("Sam"))
```

Top-level instructions are statements outside function and class definitions.
Python runs these instructions the first time a running program imports the module.
Keep reusable modules free of input prompts and unexpected print calls.
Python sets the special variable `__name__` to `"__main__"` in the file used to start the program.
That file is called the entry point.
An `if __name__ == "__main__":` check, often called the main guard, runs its block only when the file starts the program, not when another file imports it.
For example, `greetings.py` could put a demonstration call under this check:

```python
if __name__ == "__main__":
    print(hello("Sam"))
```
The tutor runs `lesson.py` as the entry point unless the exercise says otherwise.
Use the workspace file selector to edit each file.
