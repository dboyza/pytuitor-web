# Install and inspect packages

> Internet use: The exercise and its checks run offline.
> The "Try it in your own terminal" steps download packages from the internet.

Python's **standard library** is the set of modules included with Python, such as `json` and `pathlib`.
A **third-party package** is code from someone else that you download separately, usually from **PyPI**, the Python Package Index, using **pip**, Python's package installer.

Pytuitor already includes two third-party packages, `requests` and `pytest`, so this chapter's exercises import them without any download.
Pytuitor itself never installs packages for you.

## Give each project its own packages

A virtual environment is a folder containing its own Python command and installed packages, so upgrading a package for one project cannot break another.
Create one with `python -m venv .venv`, then install by running that environment's Python:

```text
.venv/bin/python -m pip install requests          (macOS and Linux)
.venv\Scripts\python.exe -m pip install requests  (Windows)
```

Writing `python -m pip` guarantees pip installs for the Python that will run your program.
Activating the environment only makes plain `python` and `pip` refer to it in that terminal; it is optional.

## Say which versions you depend on

A **requirement** names a package and, optionally, a **version specifier**:

- `requests` accepts any version.
- `requests==2.32.3` requires exactly that version, which is called pinning.
- `requests>=2.31,<3` accepts 2.31 or newer, but not version 3.

A `requirements.txt` file lists one requirement per line; text after `#` is a comment.
`python -m pip install -r requirements.txt` installs everything listed, so others can recreate your setup.

## Check what is installed

`importlib.metadata.version(name)` returns an installed package's version as a string, or raises `PackageNotFoundError` if it is missing:

```python
from importlib.metadata import PackageNotFoundError, version

try:
    print(version("requests"))
except PackageNotFoundError:
    print("requests is not installed")
```

The name you install can differ from the name you import: you install `beautifulsoup4` but write `import bs4`.
`importlib.metadata` uses the installed name and runs none of the package's code, while trying an `import` can give the wrong answer.

Installing a package runs its author's code with your permissions.
Check the spelling and project page first, because attackers publish look-alike names such as `reqeusts`.

## Try it in your own terminal

These steps need an internet connection and run outside Pytuitor.

1. In a new practice folder, run `python -m venv .venv`.
2. Install requests with the environment's Python, using the command for your system above.
3. Write `requests>=2.31` into `requirements.txt`.
4. Delete `.venv`, recreate it, and run `python -m pip install -r requirements.txt` with its Python to rebuild your setup from the file.
