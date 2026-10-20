## Check inputs before using them
Validation means checking whether input meets your program's rules.
A function's contract describes its accepted inputs and promised results.
Check inputs when they enter the function, before other operations rely on them.
As in Math and statistical summaries, `raise ValueError("message")` deliberately reports an unacceptable value.
A caller can catch it with the `try`/`except` pattern you learned earlier.
A function that answers a yes-or-no question is often called a predicate.
It can return `True` or `False` instead of raising an error.

The Boolean operators `and`, `or`, and `not` from Making decisions are useful for combining these rules.
`part in text` asks whether one string occurs inside another.

`text.isalpha()` is true when all characters are letters and text is nonempty.
`text.isalnum()` also allows digits, including letters and digits from other languages.
Neither method accepts an underscore; allow that character explicitly when your rules need it.
