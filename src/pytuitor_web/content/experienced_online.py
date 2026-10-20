"""Build and Repair contracts for packages, pytest, and web APIs; every check runs offline."""

from textwrap import indent

from pytuitor_web.experienced_authoring import _probe, _repair, check, probe, unit
from pytuitor_web.models import code

_VERSION = "__import__('importlib.metadata', fromlist=['version']).version"
_MISSING = "no-such-package-for-pytuitor"


def _mutant_script(module, name, mutant, result):
    """Swap in a broken function and report whether the learner's tests fail.

    Each mutant breaks exactly one documented behavior, so only a test aimed at it can fail.
    """
    return (
        f"import {module}\n\n"
        + code(mutant)
        + f"original = {module}.{name}\n{module}.{name} = mutant\n"
        + "try:\n"
        + f"    code, collected, report = __pytest_run__('test_{module}.py')\n"
        + f"finally:\n    {module}.{name} = original\n"
        + f"{result} = code != 0\n"
    )


def _passing_script(module, minimum, result):
    """Run the learner's tests against their module and show pytest's report."""
    return (
        f"code, collected, report = __pytest_run__('test_{module}.py')\n"
        + "print(report)\n"
        + f"{result} = [code, collected >= {minimum}]\n"
    )


_RECORD_TIMEOUTS = """
    import requests

    timeouts = []
    original_request = requests.Session.request


    def recording(self, method, url, **options):
        timeouts.append(options.get("timeout"))
        return original_request(self, method, url, **options)


    def bounded(value):
        if value is None:
            return False
        limits = value if isinstance(value, tuple) else (value,)
        return all(0 < limit <= 10 for limit in limits)
"""

_FORECAST_SERVER = """
    def respond(method, path, query, data):
        if method == "GET" and path == "/forecast":
            city = query.get("city", "")
            if city == "Atlantis":
                return 404, {"error": "unknown city"}
            if city == "Storm":
                return 503, {"error": "busy"}
            return 200, {"city": city, "low": 3, "high": 9}
        if method == "POST" and path == "/sightings":
            if not isinstance(data, dict) or data.get("count", -1) < 0:
                return 400, {"error": "bad sighting"}
            return 201, {"id": 7}
        return 404, {"error": "no such endpoint"}
"""

_TRAIL_SERVER = """
    def respond(method, path, query, data):
        if path == "/trails/1":
            return 200, {"status": "open"}
        if path == "/trails/5":
            return 500, {"error": "database down"}
        return 404, {"error": "unknown trail"}
"""


def _web_script(server, body, result):
    """Run body against a local practice server while recording every request timeout."""
    return (
        code(_RECORD_TIMEOUTS)
        + "\n"
        + code(server)
        + "\nrequests.Session.request = recording\n"
        + "try:\n"
        + "    with __practice_server__(respond) as (base, seen):\n"
        + indent(code(body), " " * 8)
        + "finally:\n"
        + "    requests.Session.request = original_request\n"
        + f"{result} = outcome\n"
    )


def _raises_http_error(call):
    return f"""
        try:
            {call}
            outcome = "no error"
        except requests.HTTPError:
            outcome = "HTTPError"
    """


LESSONS = (
    unit(
        "installing-packages",
        "python-online",
        "Install and inspect packages",
        "pip, virtual environments & requirements",
        """
        from importlib.metadata import PackageNotFoundError, version


        def parse_requirement(line):
            text = line.split("#", 1)[0].strip()
            if not text:
                return None
            for index, character in enumerate(text):
                if character in "=<>!~":
                    return text[:index].strip(), "".join(text[index:].split())
            return text, ""


        def installed_version(name):
            try:
                return version(name)
            except PackageNotFoundError:
                return None


        def requirement_report(lines):
            report = []
            for line in lines:
                requirement = parse_requirement(line)
                if requirement is None:
                    continue
                name = requirement[0]
                found = installed_version(name)
                report.append(f"{name}: {found if found else 'missing'}")
            return report
        """,
        [
            check(
                "Read requirement lines",
                "[parse_requirement('requests==2.32.3'), "
                "parse_requirement('  pytest >= 8 , < 9  # tests'), parse_requirement('rich')]",
                [["requests", "==2.32.3"], ["pytest", ">=8,<9"], ["rich", ""]],
            ),
            check(
                "Blank lines and comments are not requirements",
                "[parse_requirement(''), parse_requirement('   '), "
                "parse_requirement('# only a comment')]",
                [None, None, None],
            ),
            check(
                "Installed and missing packages",
                f"[installed_version('requests'), installed_version('{_MISSING}')]",
                {"expr": f"[{_VERSION}('requests'), None]"},
            ),
            check(
                "The distribution name can differ from the import name",
                "installed_version('charset-normalizer') is not None",
                True,
            ),
            check(
                "A report for a requirements file",
                "requirement_report(['requests>=2.31  # web', '', '# dev tools', 'pytest', "
                f"'{_MISSING}==1.0'])",
                {
                    "expr": f"['requests: ' + {_VERSION}('requests'), "
                    f"'pytest: ' + {_VERSION}('pytest'), '{_MISSING}: missing']"
                },
            ),
        ],
        [
            "Remove any comment, then strip spaces; the name ends at the first =, <, >, !, "
            "or ~ character.",
            "importlib.metadata.version raises PackageNotFoundError for a missing package.",
        ],
    ),
    unit(
        "pytest-basics",
        "python-online",
        "Test with pytest",
        "pytest tests, parametrize & raises",
        """
        def apply_discount(price, percent):
            if price < 0:
                raise ValueError("Price cannot be negative")
            if not 0 <= percent <= 100:
                raise ValueError("Percent must be between 0 and 100")
            return round(price * (100 - percent) / 100, 2)
        """,
        [
            check(
                "Discounts are applied and rounded",
                "[apply_discount(80, 25), apply_discount(19.99, 10), apply_discount(5, 0), "
                "apply_discount(5, 100)]",
                [60, 17.99, 5, 0],
            ),
            check(
                "Invalid values raise ValueError",
                "[__raises_value_error__(lambda percent: apply_discount(10, percent), 101), "
                "__raises_value_error__(lambda percent: apply_discount(10, percent), -1), "
                "__raises_value_error__(lambda price: apply_discount(price, 10), -1)]",
                [True, True, True],
            ),
            probe(
                "Your tests pass",
                _passing_script("shop", 4, "__probe_result__"),
                [0, True],
                "Run pytest on test_shop.py against your shop.py and count the collected tests",
                "Every test must pass against your own apply_discount, with at least 4 tests "
                "collected.",
            ),
            probe(
                "Your tests notice a missing discount",
                _mutant_script(
                    "shop",
                    "apply_discount",
                    """
                    def mutant(price, percent):
                        if price < 0 or not 0 <= percent <= 100:
                            raise ValueError("invalid")
                        return price
                    """,
                    "__probe_result__",
                ),
                True,
                "Run your tests against an apply_discount that returns the price unchanged",
                "Include a case where the discount changes the price.",
            ),
            probe(
                "Your tests notice an accepted percent above 100",
                _mutant_script(
                    "shop",
                    "apply_discount",
                    """
                    def mutant(price, percent):
                        if price < 0 or percent < 0:
                            raise ValueError("invalid")
                        return round(price * (100 - percent) / 100, 2)
                    """,
                    "__probe_result__",
                ),
                True,
                "Run your tests against an apply_discount that accepts any percent above 0",
                "Use pytest.raises(ValueError) with a percent above 100.",
            ),
            probe(
                "Your tests notice missing rounding",
                _mutant_script(
                    "shop",
                    "apply_discount",
                    """
                    def mutant(price, percent):
                        if price < 0 or not 0 <= percent <= 100:
                            raise ValueError("invalid")
                        return price * (100 - percent) / 100
                    """,
                    "__probe_result__",
                ),
                True,
                "Run your tests against an apply_discount that does not round",
                "Include a case whose exact result needs rounding, such as 19.99 at 10 percent.",
            ),
        ],
        [
            "Write shop.py first, then test_shop.py with from shop import apply_discount.",
            "One parametrized test with three rows plus one pytest.raises test gives four tests.",
        ],
        files=(
            {
                "shop.py": """
                    def apply_discount(price, percent):
                        if price < 0:
                            raise ValueError("Price cannot be negative")
                        if not 0 <= percent <= 100:
                            raise ValueError("Percent must be between 0 and 100")
                        return round(price * (100 - percent) / 100, 2)
                """,
                "test_shop.py": """
                    import pytest

                    from shop import apply_discount


                    @pytest.mark.parametrize(
                        "price, percent, expected",
                        [(80, 25, 60), (5, 0, 5), (5, 100, 0), (19.99, 10, 17.99)],
                    )
                    def test_apply_discount(price, percent, expected):
                        assert apply_discount(price, percent) == expected


                    def test_rejects_percent_above_100():
                        with pytest.raises(ValueError):
                            apply_discount(10, 150)
                """,
            },
        ),
        entrypoint="shop.py",
    ),
    unit(
        "web-requests",
        "python-online",
        "Call a web API with requests",
        "HTTP, JSON APIs & requests",
        """
        import requests


        def fetch_forecast(base_url, city):
            response = requests.get(f"{base_url}/forecast", params={"city": city}, timeout=5)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return f"{data['city']}: {data['low']} to {data['high']}"


        def post_sighting(base_url, animal, count):
            response = requests.post(
                f"{base_url}/sightings", json={"animal": animal, "count": count}, timeout=5
            )
            response.raise_for_status()
            return response.json()["id"]
        """,
        [
            probe(
                "Forecast for a known city",
                _web_script(
                    _FORECAST_SERVER, 'outcome = fetch_forecast(base, "Oslo")', "__probe_result__"
                ),
                "Oslo: 3 to 9",
                "fetch_forecast(practice server, 'Oslo'), where the server answers "
                "{'city': 'Oslo', 'low': 3, 'high': 9}",
                "Request /forecast with params={'city': city} and read response.json().",
            ),
            probe(
                "City names are sent safely",
                _web_script(
                    _FORECAST_SERVER,
                    'outcome = [fetch_forecast(base, "Bergen & Co"), seen[-1]["query"]]',
                    "__probe_result__",
                ),
                ["Bergen & Co: 3 to 9", {"city": "Bergen & Co"}],
                "fetch_forecast(practice server, 'Bergen & Co'), then the query the server "
                "received",
                "Let params encode the city; joining it into the URL breaks on & and spaces.",
            ),
            probe(
                "An unknown city returns None",
                _web_script(
                    _FORECAST_SERVER,
                    'outcome = fetch_forecast(base, "Atlantis")',
                    "__probe_result__",
                ),
                None,
                "fetch_forecast(practice server, 'Atlantis'), where the server answers 404",
                "Check for status 404 before calling raise_for_status().",
            ),
            probe(
                "Server trouble raises HTTPError",
                _web_script(
                    _FORECAST_SERVER,
                    _raises_http_error('fetch_forecast(base, "Storm")'),
                    "__probe_result__",
                ),
                "HTTPError",
                "fetch_forecast(practice server, 'Storm'), where the server answers 503",
                "Call response.raise_for_status() for statuses that are not a normal answer.",
            ),
            probe(
                "Post a sighting",
                _web_script(
                    _FORECAST_SERVER,
                    """
                    number = post_sighting(base, "owl", 2)
                    request = seen[-1]
                    outcome = [number, request["method"], request["path"], request["body"]]
                    """,
                    "__probe_result__",
                ),
                [7, "POST", "/sightings", {"animal": "owl", "count": 2}],
                "post_sighting(practice server, 'owl', 2), then the request the server received",
                "Send json={'animal': animal, 'count': count} and return the id from the reply.",
            ),
            probe(
                "A rejected sighting raises HTTPError",
                _web_script(
                    _FORECAST_SERVER,
                    _raises_http_error('post_sighting(base, "owl", -1)'),
                    "__probe_result__",
                ),
                "HTTPError",
                "post_sighting(practice server, 'owl', -1), where the server answers 400",
                "Call response.raise_for_status() after posting.",
            ),
            probe(
                "Every request has a timeout",
                _web_script(
                    _FORECAST_SERVER,
                    """
                    fetch_forecast(base, "Oslo")
                    post_sighting(base, "owl", 1)
                    outcome = [len(timeouts), all(bounded(value) for value in timeouts)]
                    """,
                    "__probe_result__",
                ),
                [2, True],
                "Record the timeout of every request made by fetch_forecast and post_sighting",
                "Pass timeout= with a value of at most 10 seconds to every request.",
            ),
        ],
        [
            "Build the URL from base_url and the path; give the city through params.",
            "Return None for 404, then call raise_for_status() before reading JSON.",
            "Use requests.post with json= and timeout=, and return response.json()['id'].",
        ],
    ),
)

BUILD_INSTRUCTIONS = {
    "installing-packages": (
        "Define three functions that read a requirements file's lines and report what is "
        "installed.\n"
        "`parse_requirement(line)` ignores everything after `#` and surrounding spaces, and "
        "returns `None` for a line left empty.\n"
        "Otherwise it returns a tuple `(name, specifier)`.\n"
        "The name is the text before the first `=`, `<`, `>`, `!`, or `~` character, without "
        "surrounding spaces.\n"
        "The specifier is the rest with every space removed, or `''` when there is none.\n"
        "For example, `'pytest >= 8 , < 9  # tests'` gives `('pytest', '>=8,<9')`.\n"
        "`installed_version(name)` returns the installed version of the distribution `name` as "
        "a string, or `None` when it is not installed.\n"
        "Use `importlib.metadata` rather than importing the package.\n"
        "`requirement_report(lines)` returns one string per requirement in order, skipping "
        "blank and comment lines: `NAME: VERSION` when installed, or `NAME: missing`.\n"
        "Pytuitor includes `requests` and `pytest`, so they report as installed; nothing in "
        "this exercise downloads or installs packages."
    ),
    "pytest-basics": (
        "Create two files.\n"
        "In `shop.py`, define `apply_discount(price, percent)`, which returns `price` reduced "
        "by `percent` percent, rounded to 2 decimal places with `round()`.\n"
        "It raises `ValueError` when `price` is negative or when `percent` is outside 0 to 100, "
        "inclusive.\n"
        "In `test_shop.py`, write pytest tests that import `apply_discount` from `shop`.\n"
        "Include one test decorated with `@pytest.mark.parametrize` with at least three "
        "`(price, percent, expected)` rows.\n"
        "One row must need rounding, such as `19.99` at `10` percent giving `17.99`.\n"
        "Include at least one test using `pytest.raises(ValueError)` for a percent above 100.\n"
        "Check runs your tests with pytest, and they must pass against your `shop.py`.\n"
        "They must also fail against three deliberately broken versions: one that ignores the "
        "discount, one that accepts a percent above 100, and one that skips rounding.\n"
        "Run executes `shop.py`."
    ),
    "web-requests": (
        "Define two functions that talk to a weather API.\n"
        "`base_url` is the server's address without a trailing slash, such as "
        "`http://127.0.0.1:8000`.\n"
        "Checks supply a practice server on your own computer, so no internet is needed.\n"
        "`fetch_forecast(base_url, city)` sends a GET request to `BASE_URL/forecast` with the "
        "city as the `city` query value.\n"
        "For status 404 it returns `None`, and for any other error status it raises "
        "`requests.HTTPError`.\n"
        "Otherwise the reply is JSON such as `{'city': 'Oslo', 'low': 3, 'high': 9}`, and it "
        "returns `CITY: LOW to HIGH`, such as `Oslo: 3 to 9`.\n"
        "`post_sighting(base_url, animal, count)` sends a POST request to `BASE_URL/sightings` "
        "with the JSON body `{'animal': ANIMAL, 'count': COUNT}`.\n"
        "For an error status it raises `requests.HTTPError`; otherwise it returns the `id` "
        "value from the JSON reply.\n"
        "Every request must set a timeout of at most 10 seconds.\n"
        "City names can contain spaces and symbols such as `&`."
    ),
}

REPAIR_STAGES = {
    "installing-packages": _repair(
        "Repair `missing_packages(names)`.\n"
        "`names` is a list of distribution names, the names you would give to pip.\n"
        "Return the names that are not installed, in their original order.\n"
        "Check installed distributions with `importlib.metadata` rather than importing the "
        "packages.\n"
        "A distribution's import name can differ from its distribution name, and importing runs "
        "the package's code.",
        """
        from importlib.metadata import PackageNotFoundError, version


        def missing_packages(names):
            missing = []
            for name in names:
                try:
                    version(name)
                except PackageNotFoundError:
                    missing.append(name)
            return missing
        """,
        """
        def missing_packages(names):
            missing = []
            for name in names:
                try:
                    __import__(name)
                except ImportError:
                    missing.append(name)
            return missing
        """,
        [
            _probe(
                "Installed packages with different import names",
                f"result = missing_packages(['requests', 'charset-normalizer', '{_MISSING}'])",
                [_MISSING],
                "charset-normalizer is installed but imported as charset_normalizer.",
            ),
            _probe(
                "Nothing missing",
                "result = missing_packages(['pytest', 'requests'])",
                [],
                "Ask importlib.metadata about the distribution name.",
            ),
            _probe(
                "No names",
                "result = missing_packages([])",
                [],
                "An empty list has nothing missing.",
            ),
        ],
        (
            "Compare the name you install, charset-normalizer, with the name you import.",
            "importlib.metadata.version(name) raises PackageNotFoundError for a missing "
            "distribution.",
        ),
    ),
    "pytest-basics": _repair(
        "Repair the tests in `test_shop.py`, not `shop.py`.\n"
        "`shop.py` is correct: `total(prices)` returns the sum rounded to 2 decimal places, "
        "returns `0` for an empty list, and raises `ValueError` for a negative price.\n"
        "pytest must discover and run at least three tests, and they must all pass.\n"
        "Together, the tests must fail against broken versions of `total` that add up the wrong "
        "prices, return `None` for an empty cart, or accept a negative price.",
        "",
        "",
        [
            _probe(
                "The tests run and pass",
                _passing_script("shop", 3, "result"),
                [0, True],
                "pytest discovers only functions whose names start with test_.",
            ),
            _probe(
                "The tests notice a wrong total",
                _mutant_script(
                    "shop",
                    "total",
                    """
                    def mutant(prices):
                        if any(price < 0 for price in prices):
                            raise ValueError("negative")
                        return round(sum(prices[1:]), 2)
                    """,
                    "result",
                ),
                True,
                "A comparison without assert checks nothing.",
            ),
            _probe(
                "The tests notice an empty cart returning None",
                _mutant_script(
                    "shop",
                    "total",
                    """
                    def mutant(prices):
                        if any(price < 0 for price in prices):
                            raise ValueError("negative")
                        if not prices:
                            return None
                        return round(sum(prices), 2)
                    """,
                    "result",
                ),
                True,
                "Is the empty-cart test ever discovered?",
            ),
            _probe(
                "The tests notice an accepted negative price",
                _mutant_script(
                    "shop",
                    "total",
                    """
                    def mutant(prices):
                        return round(sum(prices), 2)
                    """,
                    "result",
                ),
                True,
                "Put the call that should fail inside the pytest.raises block.",
            ),
        ],
        (
            "Read pytest's report: how many tests ran, and which one failed?",
            "Check each test's name, each comparison's assert, and what sits inside pytest.raises.",
        ),
        files=(
            {
                "shop.py": """
                    def total(prices):
                        for price in prices:
                            if price < 0:
                                raise ValueError("Prices cannot be negative")
                        return round(sum(prices), 2)
                """,
                "test_shop.py": """
                    import pytest

                    from shop import total


                    def test_empty_cart():
                        assert total([]) == 0


                    def test_sum():
                        assert total([1.5, 2.25]) == 3.75


                    def test_negative_price():
                        with pytest.raises(ValueError):
                            total([-1])
                """,
            },
            {
                "shop.py": """
                    def total(prices):
                        for price in prices:
                            if price < 0:
                                raise ValueError("Prices cannot be negative")
                        return round(sum(prices), 2)
                """,
                "test_shop.py": """
                    import pytest

                    from shop import total


                    def check_empty_cart():
                        assert total([]) == 0


                    def test_sum():
                        total([1.5, 2.25]) == 3.75


                    def test_negative_price():
                        with pytest.raises(ValueError):
                            pass
                        total([-1])
                """,
            },
        ),
    ),
    "web-requests": _repair(
        "Repair `trail_status(base_url, trail_id)`, which sends a GET request to "
        "`BASE_URL/trails/TRAIL_ID`.\n"
        "For status 404 it returns `None`, and for any other error status it raises "
        "`requests.HTTPError`.\n"
        "Otherwise it returns the `status` value from the JSON reply, such as `open`.\n"
        "The request must set a timeout of at most 10 seconds.\n"
        "Checks use a practice server on your own computer.",
        """
        import requests


        def trail_status(base_url, trail_id):
            response = requests.get(f"{base_url}/trails/{trail_id}", timeout=5)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()["status"]
        """,
        """
        import requests


        def trail_status(base_url, trail_id):
            response = requests.get(f"{base_url}/trails/{trail_id}")
            data = response.json()
            return data.get("status")
        """,
        [
            _probe(
                "An open trail",
                _web_script(_TRAIL_SERVER, "outcome = trail_status(base, 1)", "result"),
                "open",
                "Read the status value from response.json().",
            ),
            _probe(
                "An unknown trail returns None",
                _web_script(_TRAIL_SERVER, "outcome = trail_status(base, 9)", "result"),
                None,
                "Check for status 404 before reading the reply.",
            ),
            _probe(
                "A server error raises HTTPError",
                _web_script(_TRAIL_SERVER, _raises_http_error("trail_status(base, 5)"), "result"),
                "HTTPError",
                "An error reply is still a response; raise_for_status() turns it into an error.",
            ),
            _probe(
                "The request has a timeout",
                _web_script(
                    _TRAIL_SERVER,
                    """
                    trail_status(base, 1)
                    outcome = [len(timeouts), all(bounded(value) for value in timeouts)]
                    """,
                    "result",
                ),
                [1, True],
                "Without timeout=, a silent server can make the program wait forever.",
            ),
        ],
        (
            "Ask the practice server for trail 5 and compare what you get with an open trail.",
            "Which line would stop the program from waiting forever on a silent server?",
        ),
    ),
}

EXTRA_CHECKS = {}
