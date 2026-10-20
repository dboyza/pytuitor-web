## Give a parameter a default
A parameter can have a default value when the caller leaves it out.

```python
def repeat_word(word, times=2):
    return word * times


print(repeat_word("ha"))
print(repeat_word("ha", times=3))
```

Multiplying a string by an integer repeats the string that many times.
The first call returns `"haha"`; the second returns `"hahaha"`.
`times=3` is a keyword argument, like `start=1` in `enumerate()`: it names the parameter receiving that value.
Required parameters go before parameters with defaults.
A variable assigned inside a function is normally **local**: it belongs to that function call.
An **accumulator** is a variable that keeps a running result, such as a total.
Start the total at zero inside the function so each call calculates its own result.
