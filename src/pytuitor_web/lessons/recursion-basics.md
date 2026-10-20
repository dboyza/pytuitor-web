## A function can call itself
Recursion solves a problem by asking the same function to solve a smaller problem.
A base case returns immediately, without another recursive call.
Every other call must move toward that base case.

```python
def countdown(number):
    if number == 0:
        return "go"
    return str(number) + " " + countdown(number - 1)


print(countdown(3))  # 3 2 1 go
```

`countdown(3)` waits for `countdown(2)`, which waits for `countdown(1)`, which waits for `countdown(0)`.
The final call returns `"go"`, then each waiting call builds its result.
Each call has its own local `number`.
Without a reachable base case, Python eventually raises `RecursionError` because too many calls are waiting.
Use a loop for very long linear sequences; recursion is especially useful for nested structures, which come next.
