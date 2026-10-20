## Keep data after the program ends
Variables disappear when a program exits; files can keep data for another run.
A file path tells Python where to find a file, for example `"message.txt"` in the folder where the program runs.
A text encoding describes how characters are stored as bytes, the small units of data in a file.
UTF-8 is a common encoding that supports characters from many languages.
`open(path, "r", encoding="utf-8")` opens a text file for reading.
`"w"` opens it for writing and replaces existing contents, so choose the path carefully.
A `with` statement closes the file when its indented block finishes, including if an error occurs.
The open file supports context management: Python sets it up for the block and closes it afterward.
In `with open(...) as handle:`, `handle` is the name used to read or write that open file inside the block.

```python
with open("message.txt", "w", encoding="utf-8") as handle:
    handle.write("See you tomorrow\n")

with open("message.txt", "r", encoding="utf-8") as handle:
    message = handle.read()
print(message)
```

In Python source, `\n` inside a string represents a newline character.
`.read()` returns the file's entire contents as a string.
`.splitlines()` turns that string into a list of lines without newline characters.
Trying to read a missing file raises `FileNotFoundError`.
We will supply existing files for this exercise.

Run executes your program in this stage's workspace folder, the same folder the terminal opens in.
Files your program creates or changes stay there, so later runs can read them.
New files appear under Other files in the file list; add one to the workspace to edit it and include it in checks.
Check copies only your workspace files into a fresh folder, so it never sees or keeps files from earlier runs.
Binary files, such as images, do not contain ordinary text.
Symbolic links point to another file or folder instead of containing their own data.
Those files, and files beyond the workspace limits, are omitted from the preview.
For experiments with those files, export the workspace and run it in a folder you control.
