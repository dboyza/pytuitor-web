"""Plausible wrong answers and independent correct approaches from the content review."""

import pytest

from pytuitor_web.curriculum import BY_ID
from pytuitor_web.runner import execute

MUTANTS = [
    ("managed-contexts", "return False", "return True"),
    ("iterator-recipes", "zip_longest(left, right,", "zip_longest(list(left), list(right),"),
    ("ready-to-ship", "def test_parse_percentage():", "def test_parse_percentage():\n    return\n"),
    ("descriptors", "return self", "return None"),
    ("objects-not-boxes", "result.update(deepcopy(overrides))", "result.update(overrides)"),
    ("functions-with-memory", "tuple(sorted(kwargs.items()))", "tuple(kwargs.items())"),
    ("data-models", "@dataclass(frozen=True)", "@dataclass"),
    ("dataclass-lifecycle", "return replace(self, labels=[*self.labels, label])", "return self"),
    ("coroutine-basics", "await asyncio.sleep(0)", "pass"),
    ("class-construction", "return cls(base)", "return IntegerDecoder(base)"),
    ("class-construction", "2 <= value <= 36", "2 < value < 36"),
    ("method-resolution", "super().__init__(**kwargs)", "Root.__init__(self)"),
    (
        "package-metadata",
        "return tomllib.loads(text)['project'].get('requires-python')",
        "try:\n        return tomllib.loads(text)['project'].get('requires-python')\n"
        "    except Exception:\n        return None",
    ),
]


@pytest.mark.parametrize("identifier,old,new", MUTANTS, ids=[row[0] for row in MUTANTS])
async def test_incorrect_repairs_are_rejected(identifier, old, new):
    lesson = BY_ID[identifier]
    repair = lesson.stage_contract("repair")
    files = dict(repair.reference_files)
    assert old in files[lesson.entrypoint]
    files[lesson.entrypoint] = files[lesson.entrypoint].replace(old, new)
    result = await execute(lesson, files[lesson.entrypoint], files=files, stage=repair)
    assert not result.passed
    assert any(not case.get("passed", False) for case in result.checks)


ALTERNATIVES = {
    "python-expressions": """
def format_label(name, count):
    if name is None:
        display = 'Anonymous'
    else:
        display = name.strip()
        if display == '':
            display = 'Anonymous'
    return display + ': ' + str(count)
""",
    "collection-idioms": """
def count_words(words):
    result = {}
    for word in words:
        if word not in result:
            result[word] = 0
        result[word] += 1
    return result
""",
    "iterator-tools": """
def windowed(items, size):
    if size <= 0:
        raise ValueError('invalid size')
    window = []
    for value in items:
        window.append(value)
        if len(window) > size:
            del window[0]
        if len(window) == size:
            yield tuple(window)
""",
    "iterator-recipes": """
def interleave(left, right):
    left, right = iter(left), iter(right)
    while True:
        try:
            yield next(left)
        except StopIteration:
            yield from right
            return
        try:
            yield next(right)
        except StopIteration:
            yield from left
            return
""",
    "functional-pipelines": """
def partition(items, predicate):
    yes = []
    no = []
    for item in items:
        if predicate(item):
            yes.append(item)
        else:
            no.append(item)
    return yes, no
""",
}


@pytest.mark.parametrize("identifier,source", ALTERNATIVES.items(), ids=ALTERNATIVES)
async def test_alternative_correct_repairs_pass(identifier, source):
    lesson = BY_ID[identifier]
    stage = lesson.stage_contract("repair")
    result = await execute(lesson, source, stage=stage)
    assert result.passed, (result.error, result.checks)
