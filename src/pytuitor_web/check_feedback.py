"""A concise selected-case view with complete evidence available on request."""


def status(case):
    return "RUNNING" if case["status"] == "running" else "PASS" if case["passed"] else "FAIL"


def selected_case(checks, selected=None):
    if selected in checks:
        return checks[selected]
    return next(
        (case for case in checks.values() if case.get("passed") is False),
        next(iter(checks.values()), None),
    )


def render_feedback(checks, selected, *, details=False, stage="Build", compact=False):
    if not checks:
        return ""
    passed = sum(case.get("passed", False) for case in checks.values())
    case = selected_case(checks, selected)
    lines = [
        f"{stage.upper()} · {passed}/{len(checks)} checks passed",
        "",
        f"{case['number']}. {status(case)} · {case['label']}",
        f"Test: {case['operation']}",
    ]
    if compact:
        lines = [f"{passed}/{len(checks)} passed · {status(case)} · {case['label']}"]
        if details:
            lines.append(f"Test: {case['operation']}")
    observations = case.get("observations", [])
    evidence = next((item for item in observations if not item["passed"]), None)
    if evidence:
        relation = evidence["comparison"]
        lines += [
            evidence["label"],
            f"Expected result: {relation} {evidence['expected']}",
            f"Actual result: {evidence['actual']}",
        ]
    else:
        lines.append(f"Expected result: {case['expected']}")
        if case["status"] == "finished":
            lines.append(f"Actual result: {case['actual']}")
    if case.get("passed") is False:
        lines.append(f"Hint: {case['nudge']}")
    if details:
        lines += [
            "",
            "Keyboard input: " + (case["input"].replace("\n", " ↵ ").rstrip() or "none"),
            "Expected printed output: "
            + (
                repr(case["expected_output"])
                if case.get("expected_output") is not None
                else "not required; this case checks behavior or a return value"
            ),
            "Printed output: " + repr(case.get("output", "")),
        ]
        for observation in observations:
            lines += [
                f"{'PASS' if observation['passed'] else 'FAIL'} · {observation['label']}",
                f"  Expected {observation['comparison']} {observation['expected']}",
                f"  Actual {observation['actual']}",
            ]
    footer = [
        "",
        f"{len(checks)} {'case' if len(checks) == 1 else 'cases'} available in Checks. "
        + (
            "Hide details for a shorter view."
            if details
            else "Details shows input and printed output."
        ),
    ]
    if not compact:
        lines += footer
    return "\n".join(lines)
