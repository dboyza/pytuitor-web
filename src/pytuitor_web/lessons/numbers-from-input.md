## Text must become a number before arithmetic
`input()` always gives you a string, including when someone types digits.
Use `int()` to convert a whole-number string into an integer.
You can store the result in another variable.

```python
boxes_text = input("Boxes: ")
boxes = int(boxes_text)
bottles = boxes * 6
print(bottles)
```

Typing `4` prints `24`.
Typing `four` raises a `ValueError` because it cannot be converted to an integer.
For now, our exercise inputs will always be valid whole numbers.
We will handle invalid answers in a later lesson.

`//` divides and rounds down to a whole number.
`%` gives the remainder after division.
For example, `17 // 5` is `3`, while `17 % 5` is `2`.
Ordinary `/` division gives a decimal number, called a `float`, even when the division is exact.

## Practice in the workspace

Use the active exercise panel beside the editor for the current task requirements and input examples.
Use Run to try boundary values such as zero and an exact multiple of 60.
Use Check to compare your stored values and printed output with several cases.
