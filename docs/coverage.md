# Topic coverage

Use this index to find lessons by Python topic.
For the recommended sequence and advisory prerequisites, see the [curriculum map](curriculum.md).
Pytuitor has 84 teaching lessons and 22 cumulative Lantern Reach milestones.
Lessons use blank Build followed by Repair; game milestones use cumulative Extend followed by an independent Repair.
See [the growing game guide](lantern-reach.md) for continuity, checkpoints, and optional extensions.

Each linked lesson contains an explanation, worked examples, a required exercise, and executable checks.
The focus column describes what is taught across those lessons; not every API mentioned in prose is independently required by a check.

| Python topic | Pytuitor lessons | Coverage focus |
|---|---|---|
| variables | [Variables and input](../src/pytuitor_web/lessons/names-and-voices.md), [Objects and copying](../src/pytuitor_web/lessons/objects-not-boxes.md) | Assignment, conversion, identity, aliasing, mutability |
| strings | [Cleaning strings](../src/pytuitor_web/lessons/clean-labels.md), [Decimal measurements](../src/pytuitor_web/lessons/decimal-measurements.md) | String methods, normalization, splitting, f-strings and formatting |
| conditionals | [Making decisions](../src/pytuitor_web/lessons/choose-a-door.md), [Expressions](../src/pytuitor_web/lessons/python-expressions.md) | Comparisons, branching, truthiness, Boolean expressions |
| loops | [Lists and loops](../src/pytuitor_web/lessons/pack-your-bag.md), [Loop helpers](../src/pytuitor_web/lessons/loop-helpers.md), [Nested lists](../src/pytuitor_web/lessons/nested-collections.md), [While loops](../src/pytuitor_web/lessons/repeat-until-done.md) | For/while loops, range, enumerate, zip, nested traversal, stopping conditions |
| functions | [Writing functions](../src/pytuitor_web/lessons/small-superpowers.md), [Function options](../src/pytuitor_web/lessons/function-options.md), [Call contracts](../src/pytuitor_web/lessons/call-contracts.md) | Parameters, return values, defaults, keyword and positional arguments, debugging |
| lists | [List positions](../src/pytuitor_web/lessons/list-positions.md), [Editing collections](../src/pytuitor_web/lessons/editing-collections.md), [Nested lists](../src/pytuitor_web/lessons/nested-collections.md), [Summarizing lists](../src/pytuitor_web/lessons/summary-builtins.md) | Indexing, empty lists, insertion/removal, sorting, nested and ragged data; sum, max, min, any, and all |
| tuples | [Tuples and sets](../src/pytuitor_web/lessons/tuples-and-sets.md), [Loop helpers](../src/pytuitor_web/lessons/loop-helpers.md) | Ordered fixed groups, unpacking, tuple-producing iteration |
| dictionaries | [Dictionaries and counts](../src/pytuitor_web/lessons/word-counts.md), [Editing collections](../src/pytuitor_web/lessons/editing-collections.md), [Dictionary pairs](../src/pytuitor_web/lessons/dictionary-pairs.md) | Key/value access, counting, defaults, deletion, dictionary views; keys, values, and items loops |
| sets | [Tuples and sets](../src/pytuitor_web/lessons/tuples-and-sets.md), [Comparing sets](../src/pytuitor_web/lessons/comparing-sets.md) | Uniqueness, membership, union, intersection, differences, subsets |
| comprehensions | [Readable comprehensions](../src/pytuitor_web/lessons/comprehensions.md), [Collection idioms](../src/pytuitor_web/lessons/collection-idioms.md) | Transformation, filtering, dictionary/set comprehensions, order |
| exceptions | [Invalid input](../src/pytuitor_web/lessons/handle-invalid-input.md), [Exceptions with context](../src/pytuitor_web/lessons/exception-boundaries.md) | Recovery, custom errors, exception chaining, cleanup and propagation |
| file_io | [Text files](../src/pytuitor_web/lessons/text-files.md), [CSV tables](../src/pytuitor_web/lessons/csv-tables.md), [Safe copying](../src/pytuitor_web/lessons/copy-with-care.md) | Context-managed text files, structured tables, non-overwriting writes |
| classes | [Your first class](../src/pytuitor_web/lessons/your-first-class.md), [Object protocols](../src/pytuitor_web/lessons/practical-object-protocols.md), [Class construction](../src/pytuitor_web/lessons/class-construction.md), [Inheritance and polymorphism](../src/pytuitor_web/lessons/object-principles.md) | Instance state, properties, representations, length, equality, operators, factories; encapsulation, abstraction, inheritance, overriding, super(), and polymorphism |
| functional | [Callable tools](../src/pytuitor_web/lessons/callable-tools.md), [Functional pipelines](../src/pytuitor_web/lessons/functional-pipelines.md) | Function values, lambdas, sorting keys, partial application, map/filter/reduce |
| decorators | [Arguments and decorators](../src/pytuitor_web/lessons/functions-with-memory.md), [Decorator factories](../src/pytuitor_web/lessons/decorator-factories.md) | Closures, argument forwarding, metadata, configured and stacked decorators |
| generators | [Iterators and generators](../src/pytuitor_web/lessons/lazy-by-design.md), [Iterator tools](../src/pytuitor_web/lessons/iterator-tools.md) | Yield, lazy consumption, iterator exhaustion, independent yielded values |
| context_managers | [Restore temporary state](../src/pytuitor_web/lessons/context-practice.md), [Context protocol](../src/pytuitor_web/lessons/managed-contexts.md) | Generator and class context managers, entry/exit, cleanup, suppression |
| dataclasses | [Value objects](../src/pytuitor_web/lessons/data-models.md), [Dataclass lifecycle](../src/pytuitor_web/lessons/dataclass-lifecycle.md) | Generated methods, value equality, mutable defaults, post-init validation, replacement |
| type_hints | [Types and tests](../src/pytuitor_web/lessons/ready-to-ship.md), [Typed contracts](../src/pytuitor_web/lessons/typed-contracts.md), [Protocols](../src/pytuitor_web/lessons/structural-typing.md) | Annotations, unions, aliases, generic relationships, structural typing |
| regex | [Matching patterns](../src/pytuitor_web/lessons/regex-validation.md), [Extracting and replacing](../src/pytuitor_web/lessons/regex-transformations.md) | Whole-string matching, groups, character classes, extraction and substitution |
| testing | [Automated tests](../src/pytuitor_web/lessons/tests-for-your-code.md), [Types and tests](../src/pytuitor_web/lessons/ready-to-ship.md), [Test doubles](../src/pytuitor_web/lessons/test-doubles.md), [Test with pytest](../src/pytuitor_web/lessons/pytest-basics.md) | Assertions, unittest, boundaries, dependency injection, mocking; pytest discovery, parametrize, raises, and fixtures |
| recursion | [Base cases](../src/pytuitor_web/lessons/recursion-basics.md), [Recursive collections](../src/pytuitor_web/lessons/recursive-collections.md) | Stopping conditions, shrinking inputs, nested traversal and limits |
| modules | [Your own modules](../src/pytuitor_web/lessons/your-own-modules.md), [Module boundaries](../src/pytuitor_web/lessons/module-boundaries.md), [Numeric tools](../src/pytuitor_web/lessons/numeric-tools.md), [Randomness](../src/pytuitor_web/lessons/repeatable-randomness.md) | Imports, reusable modules, math/statistics, independent seeded generators |
| collections | [Counting and grouping](../src/pytuitor_web/lessons/counting-and-grouping.md), [Queues](../src/pytuitor_web/lessons/queues-with-deque.md) | Counter, defaultdict, deque, ordering and mutation boundaries |
| itertools | [Iterator tools](../src/pytuitor_web/lessons/iterator-tools.md), [Iterator recipes](../src/pytuitor_web/lessons/iterator-recipes.md), [Adjacent groups](../src/pytuitor_web/lessons/adjacent-groups.md) | islice, chain, zip_longest, product, groupby and one-pass group lifetimes |
| json | [Structured data](../src/pytuitor_web/lessons/json-records.md) | JSON reading/writing and structured-data transformation |
| datetime | [Dates and deadlines](../src/pytuitor_web/lessons/dates-and-deadlines.md), [Dates and times](../src/pytuitor_web/lessons/date-time-formats.md) | Date arithmetic, parsing, formatting, combining clock/calendar values, leap days |
| enums | [Named states](../src/pytuitor_web/lessons/named-states.md) | Named members, value conversion, validated state transitions |
| pathlib | [Paths and folders](../src/pytuitor_web/lessons/paths-and-folders.md), [Resource paths](../src/pytuitor_web/lessons/resource-paths.md) | Path composition, file queries, explicit roots, safe automation |
| oop_advanced | [Class construction](../src/pytuitor_web/lessons/class-construction.md), [Descriptors](../src/pytuitor_web/lessons/descriptors.md), [Metaclasses](../src/pytuitor_web/lessons/metaclasses.md), [Method resolution](../src/pytuitor_web/lessons/method-resolution.md) | Abstract interfaces, class/static methods, descriptors, class hooks, cooperative inheritance |
| async | [Coroutines](../src/pytuitor_web/lessons/coroutine-basics.md), [Task groups](../src/pytuitor_web/lessons/task-groups.md), [Async streams](../src/pytuitor_web/lessons/async-streams.md) | Await, resource lifetimes, cancellation, async iteration |
| pattern_matching | [Match values by their shape](../src/pytuitor_web/lessons/pattern-matching.md) | match and case with literal, capture, sequence, mapping, and wildcard patterns, guards, and case order |
| logging | [Logging](../src/pytuitor_web/lessons/logging-basics.md) | Named loggers, levels, argument formatting, application-only configuration, and exception records |
| databases | [SQLite records](../src/pytuitor_web/lessons/sqlite-records.md) | sqlite3 tables, placeholders against SQL injection, transactions, and queries |
| packages | [Install and inspect packages](../src/pytuitor_web/lessons/installing-packages.md) | pip, virtual environments, requirements and version specifiers, importlib.metadata; try-it steps need internet |
| web_apis | [Call a web API with requests](../src/pytuitor_web/lessons/web-requests.md) | HTTP methods, status codes, JSON APIs, requests with params, json, and timeouts; checks use a local practice server |

## Curriculum choices

Practical collection operations and ordinary class protocols precede specialized machinery.
One syllabus groups the curriculum into Foundations, Everyday Python, Building programs, Python depth, Specialized topics, and Online and third-party.
The first three sections are recommended; the other three are optional.
Descriptors, class hooks, and cooperative inheritance remain available for learners who need language machinery.
Each of the 22 chapters ends with a cumulative game milestone.
See the [curriculum map](curriculum.md) for chapter order and advisory prerequisites.
The topic map is a maintenance aid; learner studies are required to assess retention and transfer to unfamiliar problems.
