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

The tutor runs your code in temporary copies of the workspace.
When Run creates or changes eligible text files, a **Run files** button appears in the console.
Open it to inspect each file, then choose **Save to workspace** to keep the files for later runs or exports.
Saving first backs up your current stage, then adds or replaces the previewed files without deleting other files.
Files are not saved automatically, and Check always discards its file changes.
Binary files, such as images, do not contain ordinary text.
Symbolic links point to another file or folder instead of containing their own data.
Those files, and files beyond the workspace limits, are omitted from the preview.
For experiments with those files, export the workspace and run it in a folder you control.
