# Understand package metadata

A **virtual environment** is a directory containing a Python command and installed packages kept separate from those of other projects.
It does not sandbox code or make an untrusted dependency safe.
The tutor can guide workspace environment setup; keep dependency installation deliberate and review the requested package and version first.
All exercises in this course work with the standard library after the tutor is installed.

In an external terminal, a typical project begins with `python3 -m venv .venv`.
On macOS and Linux, use `.venv/bin/python -m pip ...` to target that environment explicitly.
Avoid `sudo pip`, unknown install scripts, and copying commands you have not read.
A **dependency** is another package your program needs.
Recording exact dependency versions helps repeat an installation later.
Pip can also check a downloaded file against a recorded **hash**, a value calculated from its contents, using `--require-hashes`.
Matching a recorded version and hash identifies the file; it does not establish that the code is trustworthy.

**Metadata** describes a project, such as its name and version.
`pyproject.toml` stores metadata and settings for building an installable package.
**TOML** is a text format for settings: `[project]` starts a named table, and `name = "small-report"` assigns a field inside it.
The `[project]` table contains fields such as name, version, requires-python, dependencies, and scripts.
The **build backend** is the tool that turns source files into a **wheel**, the `.whl` file used to install a Python distribution.
A distribution is the collection of code and metadata delivered for installation.
A package name used for installation is not always the same as its import name.

```toml
[project]
name = "small-report"
version = "0.2.0"
requires-python = ">=3.11"
dependencies = []
```

Use `import tomllib` to load Python's standard-library TOML reader, available since Python 3.11.
`tomllib.loads(text)` parses TOML text to dictionaries and lists.
For the example above, `tomllib.loads(text)["project"]["name"]` is `"small-report"`.
`project.get("dependencies", [])` supplies an empty list when that field is absent.
It does not install packages or evaluate arbitrary Python code.
