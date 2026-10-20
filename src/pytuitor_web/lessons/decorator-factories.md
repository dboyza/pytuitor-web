# A decorator with configuration

An ordinary decorator receives a function and returns its replacement.
A decorator factory receives configuration and returns that decorator.
There are three layers: configuration, the original function, then the arguments of each call.

```python
from functools import wraps


def repeated(times):
    def decorate(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs) * times

        return wrapper

    return decorate


@repeated(2)
def cheer(name):
    return name + "!"
```

As in the previous lesson, `*args` and `**kwargs` collect the call's arguments, and using them in a call forwards those arguments.
`wraps` preserves metadata and exposes the original function as `__wrapped__`.
Stacked decorators apply bottom-up: `@outer` above `@inner` means `outer(inner(function))`.
