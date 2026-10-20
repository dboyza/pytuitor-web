"""Optional online-chapter review; every task runs offline without contacting a server."""

from pytuitor_web.content.reviews.authoring import chapter, prediction, task

ONLINE = {
    "packages-and-web": chapter(
        "packages-and-web",
        prediction(
            "An error status is still a response",
            """
                import requests

                response = requests.Response()
                response.status_code = 404
                print(response.ok)
            """,
            ("True", "False", "404"),
            1,
            "ok is True only for status codes below 400. A 404 is a normal response that "
            "reports a problem, not an exception.",
        ),
        task(
            "Repair a success check",
            "is_success(status) returns True for the success statuses 200 to 299, inclusive, "
            "and False for every other status.",
            """
                def is_success(status):
                    return 200 <= status <= 299
            """,
            [
                (
                    "Success statuses",
                    "[is_success(200), is_success(201), is_success(299)]",
                    [True, True, True],
                ),
                (
                    "Other statuses",
                    "[is_success(199), is_success(300), is_success(404), is_success(500)]",
                    [False, False, False, False],
                ),
            ],
            broken="""
                def is_success(status):
                    return 200 <= status <= 300
            """,
            hint="300 is the first redirect status, not a success; check the upper boundary.",
        ),
        task(
            "Read a pinned requirement",
            "pinned(line) returns [NAME, VERSION] for a line pinned with == such as "
            "requests==2.32.3, ignoring surrounding spaces. Any other line returns None.",
            """
                def pinned(line):
                    name, separator, version = line.strip().partition("==")
                    if not separator or not name or not version:
                        return None
                    return [name.strip(), version.strip()]
            """,
            [
                (
                    "Pinned lines",
                    "[pinned('requests==2.32.3'), pinned('  rich == 13.9.4  ')]",
                    [["requests", "2.32.3"], ["rich", "13.9.4"]],
                ),
                (
                    "Not pinned",
                    "[pinned('pytest>=8'), pinned('requests'), pinned('')]",
                    [None, None, None],
                ),
            ],
            hint="str.partition('==') splits once and reports whether == was found.",
        ),
    ),
}
