# Inspect without executing

**Introspection** means examining information about a running program's objects.
A function's `__name__` gives its name; its **signature** describes its parameters and defaults.
`inspect.signature(function)` supplies that description without calling the function.

```python
import inspect

signature = inspect.signature(lambda count, *, verbose=False: None)
for name, parameter in signature.parameters.items():
    has_default = parameter.default is not inspect.Parameter.empty
```

Each parameter object has a `kind` describing how arguments can reach it.
Compare `parameter.kind` with constants on `inspect.Parameter`:

- `POSITIONAL_ONLY`: must be supplied by position, before `/` in a function definition.
- `POSITIONAL_OR_KEYWORD`: accepts either form.
- `VAR_POSITIONAL`: gathers extra positional arguments, written `*args`.
- `KEYWORD_ONLY`: must be supplied by name, after `*` or `*args`.
- `VAR_KEYWORD`: gathers extra named arguments, written `**kwargs`.

The argument-gathering forms, `*args` and `**kwargs`, are called **variadic** because they accept a variable number of arguments, including none.
`inspect.Parameter.empty` is the special marker meaning no default was supplied; use `is` to compare with it.
A default of `None` is still a default, so it differs from this marker.
Inspection should not call the function whose interface you are describing.

The broken exercise uses `fn.__code__`, a **code object** holding information needed to run a Python function.
Its `co_varnames` includes local variable names as well as parameters, so it cannot directly answer which arguments a caller must supply.
Use the signature information for that question.

As optional further exploration, **CPython** is the most widely used Python implementation.
It translates source into **bytecode**, instructions run by its interpreter; `import dis` followed by `dis.dis(fn)` displays those instructions.
Instruction names and implementation details can change between Python versions, so they should not determine your function's behavior.
