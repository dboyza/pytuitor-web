# Define a predictable CLI

A **command-line interface (CLI)** lets someone run a program by typing its name and arguments in a terminal.
You first used `argparse` in Command-line arguments; this lesson makes its behavior a deliberate contract.
An argument list passed explicitly is easier to test than code that reads global `sys.argv` everywhere.

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("--repeat", type=int, default=1)
parser.add_argument("--loud", action="store_true")
options = parser.parse_args(["Ada", "--repeat", "2"])
```

`name` is a positional argument and `--loud` is a flag.
An **option** starts with a name such as `--repeat` and may take a value; a flag is an option whose presence switches something on.
The returned object holds parsed values as attributes such as `options.repeat`.
Here, `type=int` converts text to an integer and `default=1` supplies a value when the option is absent.
`store_true` sets a Boolean when the flag appears.
An **exit status** is the number a program reports when it ends: zero usually means success.
Argparse raises `SystemExit` after printing a usage message for invalid arguments (status two), or help for `--help` (status zero).
**Standard output (stdout)** carries normal results, usually from `print`.
**Standard error (stderr)** carries error messages separately, which helps when another program reads the results.
Reusable functions should normally return values or raise exceptions so their callers choose how to display them.
