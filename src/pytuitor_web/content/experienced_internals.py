"""Build and Repair contracts for python-internals."""

from pytuitor_web.experienced_authoring import _check, _exec, _probe, _repair, check, probe, unit

LESSONS = (
    unit(
        "descriptors",
        "python-internals",
        "Control attribute access",
        "Descriptors & attribute lookup",
        """
        class NonNegative:
            def __set_name__(self, owner, name):
                self.storage = "_" + name

            def __get__(self, instance, owner=None):
                if instance is None:
                    return self
                return getattr(instance, self.storage, 0)

            def __set__(self, instance, value):
                if value < 0:
                    raise ValueError("Value must be nonnegative")
                setattr(instance, self.storage, value)

        class Counter:
            value = NonNegative()
        """,
        [
            check(
                "Default and assignment",
                "(lambda c: (c.value, setattr(c, 'value', 4), c.value))(Counter())",
                [0, None, 4],
            ),
            check(
                "Independent instances",
                "(lambda a, b: (setattr(a, 'value', 7), b.value)[1])(Counter(), Counter())",
                0,
            ),
            check(
                "Reject negatives",
                "__raises_value_error__(lambda n: setattr(Counter(), 'value', n), -1)",
                True,
            ),
            check(
                "Class access returns descriptor", "isinstance(Counter.value, NonNegative)", True
            ),
        ],
        [
            "Store values on the owner instance, not on the shared descriptor.",
            (
                "__get__ receives instance=None for class access; return the descriptor i"
                "tself in that case."
            ),
        ],
    ),
    unit(
        "metaclasses",
        "python-internals",
        "Register classes deliberately",
        "Metaclasses & class creation",
        """
        class RegistryMeta(type):
            registry = {}

            def __new__(mcls, name, bases, namespace, **kwargs):
                cls = super().__new__(mcls, name, bases, namespace, **kwargs)
                key = namespace.get("kind")
                if key is not None:
                    if key in mcls.registry:
                        raise ValueError("Duplicate kind")
                    mcls.registry[key] = cls
                return cls
        """,
        [
            check(
                "Register an explicit kind",
                (
                    "(lambda cls: RegistryMeta.registry['csv'] is cls)(RegistryMeta('CSV'"
                    ", (), {'kind': 'csv'}))"
                ),
                True,
            ),
            check(
                "Ignore classes without a kind",
                "(RegistryMeta('Base', (), {}), RegistryMeta.registry)[1]",
                {},
            ),
            check(
                "Reject duplicate kind",
                (
                    "(RegistryMeta('First', (), {'kind':'same'}), __raises_value_error__(lambda"
                    " _: RegistryMeta('Second', (), {'kind':'same'}), None))[1]"
                ),
                True,
            ),
            check(
                "Inherited kind is not reregistered",
                (
                    "(lambda base: (RegistryMeta('Child', (base,), {}), list(RegistryMeta.regis"
                    "try))[1])(RegistryMeta('Base', (), {'kind':'base'}))"
                ),
                ["base"],
            ),
        ],
        [
            (
                "Use namespace.get rather than getattr(cls, ...) so inherited kind values"
                " do not register again."
            ),
            (
                "Create the class with super().__new__, reject duplicate explicit keys, t"
                "hen store and return the class."
            ),
        ],
    ),
    unit(
        "method-resolution",
        "python-internals",
        "Method lookup and inheritance",
        "Inheritance & super",
        """
        class Root:
            def steps(self):
                return ["root"]

        class Left(Root):
            def steps(self):
                return ["left"] + super().steps()

        class Right(Root):
            def steps(self):
                return ["right"] + super().steps()

        class Pipeline(Left, Right):
            pass
        """,
        [
            check(
                "Diamond visits each class once", "Pipeline().steps()", ["left", "right", ("root")]
            ),
            check("A single branch", "Left().steps()", ["left", "root"]),
            check(
                "Reversed branches cooperate",
                "type('Reversed', (Right, Left), {})().steps()",
                ["right", "left", "root"],
            ),
        ],
        [
            (
                "super() follows the method resolution order of the actual instance, not "
                "just the named parent."
            ),
            "Prepend your step to super().steps(); Root terminates the chain.",
        ],
    ),
    unit(
        "runtime-inspection",
        "python-internals",
        "Inspect without executing",
        "Inspect function parameters",
        """
        import inspect

        def describe_callable(fn):
            signature = inspect.signature(fn)
            required = [
                name for name, parameter in signature.parameters.items()
                if parameter.default is inspect.Parameter.empty
                and parameter.kind not in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                )
            ]
            return {
                "name": fn.__name__,
                "parameters": list(signature.parameters),
                "required": required,
            }
        """,
        [
            check(
                "Defaults and variadic parameters",
                "describe_callable(lambda x, y=2, *args, flag, **kwargs: None)",
                {
                    "name": "<lambda>",
                    "parameters": ["x", "y", "args", "flag", "kwargs"],
                    "required": ["x", "flag"],
                },
            ),
            check(
                "No parameters",
                "describe_callable(lambda: 1)",
                {"name": "<lambda>", "parameters": [], "required": []},
            ),
            check(
                "Ignore locals and never call",
                (
                    "(exec(\"def sample(a, b=1):\\n    local = a\\n    raise AssertionError('ca"
                    "lled')\", globals()), describe_callable(sample))[1]"
                ),
                {"name": "sample", "parameters": ["a", "b"], "required": ["a"]},
            ),
        ],
        [
            (
                "inspect.signature provides parameter objects in declaration order withou"
                "t calling the function."
            ),
            "A required parameter has no default and is neither *args nor **kwargs.",
        ],
    ),
)

BUILD_INSTRUCTIONS = {
    "descriptors": (
        "\nDefine the descriptor class `NonNegative` and a `Counter` class with `va"
        "lue = NonNegative()`.\nReading an unset Counter value returns zero.\nAll s"
        "upplied values are finite real numbers.\nWriting a nonnegative number stor"
        "es it for that Counter only.\nWriting a negative number raises ValueError "
        "without replacing an earlier valid value.\nClass access, `Counter.value`, "
        "returns the descriptor itself.\nUse `__set_name__` to derive a private sto"
        "rage name, allowing the descriptor pattern to work under other attribute n"
        "ames too.\nFor two new counters, setting one's value to six must leave the"
        " other's value at zero.\nNo printing is required.\n"
    ).strip(),
    "metaclasses": (
        "\nImplement `RegistryMeta(type)` with an initially empty class dictionary "
        "`registry`.\nIts `__new__` must create the class using the normal type mac"
        "hinery.\nDeclared kind values are strings or None.\nIf that class body exp"
        "licitly declares a non-None `kind` string, register the new class under th"
        "at string.\nIf the key already exists, raise `ValueError` without replacin"
        "g the existing registration.\nClasses without an explicit kind, including "
        "subclasses that only inherit one, are not registered.\nFor `class Csv(meta"
        "class=RegistryMeta): kind = 'csv'`, `RegistryMeta.registry['csv']` must be"
        " Csv itself.\nDo not define example classes at module level in your answer"
        ", since the registry must initially be empty.\nDo not print.\n"
    ).strip(),
    "method-resolution": (
        "\nDefine four classes: Root, Left, Right, and Pipeline.\nRoot has a `steps"
        "(self)` method returning `['root']`.\nLeft and Right each inherit Root and"
        " prepend their respective names, `'left'` and `'right'`, to the result of "
        "a cooperative call to the next steps method.\nPipeline inherits Left first"
        " and Right second without overriding steps.\n`Pipeline().steps()` must ret"
        "urn `['left', 'right', 'root']`.\n`Left().steps()` must still return `['le"
        "ft', 'root']`.\nReversing the bases in a new class must produce `['right',"
        " 'left', 'root']` without changing Left or Right.\nReturn a fresh list eac"
        "h time and do not print.\n`pass` is the placeholder statement for a class "
        "body that adds no behavior.\n"
    ).strip(),
    "runtime-inspection": (
        "\nWrite `describe_callable(fn)` for an ordinary Python function.\nReturn a"
        " dictionary with `name` from fn.__name__, `parameters` listing all paramet"
        "er names in declaration order, and `required` listing only parameters with"
        "out defaults that are not variadic.\nInclude required keyword-only paramet"
        "ers.\nIgnore local variables, annotations, and return values.\nNever execu"
        "te fn.\nFor `def send(message, times=1, *, destination): ...`, required is"
        " `['message', 'destination']`.\nAn argument-free function produces empty l"
        "ists.\nDo not print.\n"
    ).strip(),
}

REPAIR_STAGES = {
    "descriptors": _repair(
        (
            "Define NonEmpty and Profile. The descriptor should return an empty default"
            ", reject blank assignments, and store separate values for separate descrip"
            "tor names and instances. Profile has name and team fields, each using its "
            "own NonEmpty descriptor. Class access returns the descriptor. Instance acc"
            "ess defaults to an empty string. Nonblank strings are stored unchanged, in"
            "cluding surrounding whitespace; reject blanks with ValueError without losi"
            "ng an existing value."
        ),
        """
        class NonEmpty:
            def __set_name__(self, owner, name):
                self.storage = '_' + name
            def __get__(self, instance, owner=None):
                if instance is None:
                    return self
                return getattr(instance, self.storage, '')
            def __set__(self, instance, value):
                if not value.strip():
                    raise ValueError('Blank value')
                setattr(instance, self.storage, value)

        class Profile:
            name = NonEmpty()
            team = NonEmpty()
        """,
        """
        class NonEmpty:
            def __get__(self, instance, owner=None):
                return getattr(self, 'value', '')
            def __set__(self, instance, value):
                self.value = value

        class Profile:
            name = NonEmpty()
            team = NonEmpty()
        """,
        [
            _check(
                "Independent fields",
                "(lambda p: (p.name, p.team))((lambda p: ("
                "setattr(p, 'name', 'Ada'), setattr(p, 'team', 'Core'), p)[2])"
                "(Profile()))",
                ("Ada", "Core"),
                "Derive separate storage names in __set_name__.",
            ),
            _check(
                "Reject blank",
                "__raises_value_error__(lambda _: setattr(Profile(), 'name', '   '), None)",
                True,
                "Validate before storing a descriptor value.",
            ),
            _probe(
                "Class access and separate instances",
                (
                    """
                a, b = Profile(), Profile()
                a.name = " Ada "
                try:
                    a.name = " "
                except ValueError:
                    pass
                result = (isinstance(Profile.name, NonEmpty), a.name, b.name, b.team)
                """
                ),
                (True, " Ada ", "", ""),
                (
                    "Class access returns the descriptor, while instance values live on each in"
                    "stance."
                ),
            ),
        ],
        [
            "__set_name__ receives the attribute name once at class creation.",
            "Class access should return the descriptor itself.",
        ],
    ),
    "metaclasses": _repair(
        (
            "Define CommandMeta that registers classes with an explicit command name in"
            " registry. Reject duplicates and ignore subclasses that merely inherit a c"
            "ommand. CommandMeta.registry maps explicit non-None command values to clas"
            "ses. A duplicate raises ValueError and keeps the original class. An explic"
            "itly empty string is a valid key; absent or None commands are not register"
            "ed."
        ),
        """
        class CommandMeta(type):
            registry = {}
            def __new__(mcls, name, bases, namespace, **kwargs):
                cls = super().__new__(mcls, name, bases, namespace, **kwargs)
                command = namespace.get('command')
                if command is not None:
                    if command in mcls.registry:
                        raise ValueError('Duplicate command')
                    mcls.registry[command] = cls
                return cls
        """,
        """
        class CommandMeta(type):
            registry = {}
            def __new__(mcls, name, bases, namespace, **kwargs):
                cls = super().__new__(mcls, name, bases, namespace, **kwargs)
                mcls.registry[name] = cls
                return cls
        """,
        [
            _check(
                "Register command",
                "(lambda cls: CommandMeta.registry['build'] is cls)("
                "CommandMeta('Build', (), {'command': 'build'}))",
                True,
                "Use the explicit namespace command as the key.",
            ),
            _check(
                "Ignore inherited command",
                (
                    "(CommandMeta.registry.clear(), (lambda base: (CommandMeta('Child', (base,)"
                    ", {}), list(CommandMeta.registry)))(CommandMeta('Base', (), {'command': 'b"
                    "ase'}))[1])[1]"
                ),
                ["base"],
                "Read namespace rather than inherited attributes.",
            ),
            _probe(
                "Duplicates keep the original",
                (
                    """
                CommandMeta.registry.clear()
                original = CommandMeta("First", (), {"command": "run"})
                try:
                    CommandMeta("Second", (), {"command": "run"})
                except ValueError:
                    rejected = True
                else:
                    rejected = False
                result = (rejected, CommandMeta.registry["run"] is original)
                """
                ),
                (True, True),
                "Check for collisions before replacing the registered class.",
            ),
        ],
        [
            "Create the class before registering it.",
            "Check for a collision before assignment so the original remains.",
        ],
    ),
    "method-resolution": _repair(
        (
            "Repair cooperative initialization. Root.__init__(**kwargs) calls super()._"
            "_init__ and creates self.events as a fresh list. Audit.__init__(*, actor, "
            "**kwargs) forwards remaining arguments with super(), stores actor, then ap"
            "pends 'audit:' plus actor to events. Metrics.__init__(*, unit, **kwargs) d"
            "oes the same for unit and 'metrics:' plus unit. Both inherit Root. Report("
            "Audit, Metrics) inherits initialization. Assume actor and unit are strings"
            ". Report(actor='Ada', unit='ms').events is ['metrics:ms', 'audit:Ada']. Sw"
            "apping base order reverses those events. Do not discard unknown keywords: "
            "they must reach object and raise TypeError."
        ),
        """
    class Root:
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.events = []

    class Audit(Root):
        def __init__(self, *, actor, **kwargs):
            super().__init__(**kwargs)
            self.actor = actor
            self.events.append('audit:' + actor)

    class Metrics(Root):
        def __init__(self, *, unit, **kwargs):
            super().__init__(**kwargs)
            self.unit = unit
            self.events.append('metrics:' + unit)

    class Report(Audit, Metrics):
        pass
    """,
        """
    class Root:
        def __init__(self, **kwargs):
            self.events = []

    class Audit(Root):
        def __init__(self, *, actor, **kwargs):
            Root.__init__(self)
            self.actor = actor
            self.events.append('audit:' + actor)

    class Metrics(Root):
        def __init__(self, *, unit, **kwargs):
            Root.__init__(self)
            self.unit = unit
            self.events.append('metrics:' + unit)

    class Report(Audit, Metrics):
        pass
    """,
        [
            _probe(
                "Cooperative initialization consumes each argument",
                """
                record = Report(actor="Ada", unit="ms")
                result = (record.events, record.actor, record.unit)
                """,
                (["metrics:ms", "audit:Ada"], "Ada", "ms"),
                "Forward unconsumed keywords through super before contributing your own event.",
            ),
            _probe(
                "Reversed MRO and independent instances",
                """
                class Reverse(Metrics, Audit):
                    pass


                one = Reverse(actor="Lin", unit="s")
                two = Reverse(actor="Lin", unit="s")
                one.events.append("extra")
                result = two.events
                """,
                ["audit:Lin", "metrics:s"],
                "Follow the actual MRO and create a fresh event list for each instance.",
            ),
            _probe(
                "Unknown arguments are not swallowed",
                """
                try:
                    Report(actor="Ada", unit="ms", unknown=True)
                except TypeError:
                    result = True
                else:
                    result = False
                """,
                True,
                (
                    "Forward leftover keywords all the way to object instead of silently droppi"
                    "ng them."
                ),
            ),
        ],
        [
            "Each class consumes its own keyword and forwards the rest.",
            (
                "super follows the actual MRO. Appending after super returns records the un"
                "winding order."
            ),
        ],
    ),
    "runtime-inspection": _repair(
        (
            "Define callable_defaults(fn) using inspect.signature without calling fn. R"
            "eturn a dictionary mapping parameter names with defaults to those default "
            "values, excluding variadics. Include positional-only and keyword-only defa"
            "ults in declaration order. Preserve default objects unchanged, including N"
            "one and False. A function with no defaults returns {}."
        ),
        (
            "\n        import inspect\n\n        def callable_defaults(fn):\n          "
            "  signature = inspect.signature(fn)\n            return {\n               "
            " name: parameter.default\n                for name, parameter in signature"
            ".parameters.items()\n                if parameter.default is not inspect.P"
            "arameter.empty\n                and parameter.kind\n                not in"
            " (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)\n      "
            "      }\n        "
        ),
        """
        def callable_defaults(fn):
            return {}
        """,
        [
            _check(
                "Read defaults",
                "callable_defaults(lambda x, y=2, *, flag=False, **kwargs: None)",
                {"y": 2, "flag": False},
                "Inspect parameter defaults, not code locals.",
            ),
            _check(
                "Do not call",
                _exec(
                    """
                    def sample(x=1):
                        raise AssertionError("called")
                    result = callable_defaults(sample)
                    """
                ),
                {"x": 1},
                "Signature inspection should not execute the function.",
            ),
            _probe(
                "Default identity and parameter order",
                (
                    """
                marker = []


                def function(a=None, /, b=marker, *, flag=False):
                    raise AssertionError("called")


                values = callable_defaults(function)
                result = (
                    list(values),
                    values["a"],
                    values["b"] is marker,
                    values["flag"],
                    callable_defaults(lambda x: x),
                )
                """
                ),
                (["a", "b", "flag"], None, True, False, {}),
                "Inspect defaults without copying mutable values or excluding falsy defaults.",
            ),
        ],
        [
            "inspect.Parameter.empty marks a missing default.",
            "Exclude *args and **kwargs from the returned mapping.",
        ],
    ),
}

EXTRA_CHECKS = {
    "metaclasses": (
        probe(
            "Duplicate registration preserves the original",
            """
            original = RegistryMeta("Original", (), {"kind": "saved"})
            try:
                RegistryMeta("Duplicate", (), {"kind": "saved"})
            except ValueError:
                pass
            else:
                raise AssertionError("Duplicate accepted")
            __probe_result__ = RegistryMeta.registry["saved"] is original
            """,
            True,
            "Reject a duplicate saved kind, then verify its original class remains registered.",
            "Check for collisions before assigning to the registry.",
        ),
    ),
    "descriptors": (
        probe(
            "Failed assignment preserves prior value",
            """
            counter = Counter()
            counter.value = 5
            try:
                counter.value = -2
            except ValueError:
                pass
            __probe_result__ = counter.value
            """,
            5,
            "Set a counter to five, then reject minus two; its value must remain five.",
            "Validate before writing the private instance attribute.",
        ),
        probe(
            "Descriptor works under another name",
            """
            class Gauge:
                count = NonNegative()
                total = NonNegative()
            gauge = Gauge()
            gauge.count = 2
            gauge.total = 8
            __probe_result__ = [gauge.count, gauge.total]
            """,
            [2, 8],
            (
                "Use two NonNegative attributes named count and total on one owner; their"
                " storage must be separate."
            ),
            "Derive the storage attribute from the name given to __set_name__.",
        ),
    ),
}
