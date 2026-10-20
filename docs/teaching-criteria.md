# Chapter challenge criteria

These are authoring and review criteria, not measured claims about learner difficulty.
Lesson Build stages ask the learner to combine taught ideas from a blank editor.
Game milestones use Extend to add chapter concepts to an earlier version; see the [game authoring guidance](authoring.md#growing-game-content).
Repair must require a different decision, data flow, or observable behavior; changing names alone does not qualify.
Worked examples teach the ingredients without supplying the complete required program.
Checks exercise ordinary cases, boundaries, and the chapter's likely misconception while accepting equivalent implementations.

| Chapter | Build challenge | Repair challenge and discriminating boundary |
| --- | --- | --- |
| First programs | Combine input, conversion, arithmetic, and decisions in order. | Diagnose punctuation, values, or branch boundaries; distinguish text from calculated output. |
| Lists and sets | Choose ordered storage versus unique membership. | Preserve sequence order and duplicates where required; include empty and repeated inputs. |
| Loops and dictionaries | Accumulate and summarize a sequence without resetting state. | Correct lifetime and update order; check empty input, repeats, and independent nested lists. |
| Functions and input | Separate returned values from interaction and validate input. | Correct a second transformation or retry flow; include zero, blank, and invalid input. |
| Files and structured data | Parse and transform complete records with explicit encoding. | Distinguish file handles from text and preserve record order; test empty data and persisted contents. |
| Text patterns | Express whole-input validation and targeted replacement. | Avoid accepting a partial invalid token; test boundaries around the match. |
| Modules and library tools | Put reusable behavior in the appropriate module. | Keep imports quiet and handle varied arguments or reproducible state. |
| Dates and times | Convert a specified format and perform calendar arithmetic. | Handle month, year, and leap-day boundaries without using the current date. |
| Collection tools | Select a suitable counting or queue operation. | Preserve input ownership and ordering through a different aggregation or queue policy. |
| Classes and tested tools | Model independent state and verify public behavior. | Reject invalid transitions without mutation; learner tests must reject plausible broken implementations. |
| Careful automation | Separate selection, planning, and writes. | Protect existing data at the actual write boundary, including competing writers. |
| Think in Python | Handle truthiness, identity, and argument contracts explicitly. | Preserve nested ownership, first-seen order, and falsy values in a different operation. |
| Recursion and callables | Decompose a problem or pass behavior as a value. | Preserve base cases, call order, and one-pass input while changing the computation. |
| Decorators | Separate configuration, function decoration, and calls. | Cache correctly or attach metadata without changing the original function; test keyword order and falsy results. |
| Iterators and streaming | Produce results with bounded consumption. | Implement overlapping windows, interleaving, or incremental averages; guard the source against overconsumption. |
| Exceptions and contexts | Translate intended errors and restore resources. | Exercise actual with statements, nested state, and failed cleanup; detect suppression, not merely return values. |
| Dataclasses, types, and storage | Model immutable values and validated construction, then store records with placeholders. | Distinguish a fresh instance from shared nested state; test ineffective learner regression tests. |
| Object protocols and testing | Combine public operations, factories, and structural interfaces. | Honor subclass construction, chunked reads, unsupported operands, and narrowly triggered fallbacks. |
| Async work | Bound overlapping work and preserve result order. | Race successes or stream chunks while joining cancelled siblings; coordinate probes with events, not speed thresholds. |
| Distributable tools | Separate reusable functions from CLI behavior and metadata. | Keep parser errors visible, support option order, and verify quiet imports plus actual entry-point output. |
| Python machinery | Understand per-instance storage and class creation. | Preserve registries on rejected duplicates, support dynamic plugins, and follow a changed MRO during initialization. |
| Packages, tests, and web APIs | Inspect installed distributions, write pytest tests that fail for broken code, and call an HTTP API. | Separate distribution from import names, repair undiscovered or assertion-free tests, and handle error statuses and timeouts against a local practice server. |

## Preparation and feedback

Every required construct must be explained in the current teaching or an identified prerequisite.
Optional depth remains advisory: learners may enter directly, with links back to preparation when needed.
Async races need explicit teaching about task ownership, completion order, cancellation, and joining.
Descriptor and metaclass work needs a bridge from instance attributes, properties, and inheritance.
The four object-oriented principles are defined once in Inheritance and polymorphism and named again where later lessons use them.
Cooperative initialization needs keyword forwarding and the distinction between call order and return order.

A useful failed check identifies the misconception and the next observation to make.
Prefer “A shallow copy still shares the nested list” to “Compare actual and expected.”
A complex check should describe its scenario instead of displaying an opaque executable expression as its only explanation.
Optional predictions ask learners to anticipate behavior; they do not unlock exercises or imply mastery.

## Evidence and scope

Reference passes establish consistency with authored checks.
Mutant rejection and independent alternative solutions establish selected properties of those checks.
Neither proves the exercises are moderately challenging or establishes transfer to new problems.
Use the [learner study protocol](learner-study.md) to evaluate difficulty and transfer, and report only observed outcomes.
