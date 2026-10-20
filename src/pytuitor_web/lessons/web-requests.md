# Call a web API with requests

> Internet use: The exercise and its checks run offline: each check starts a practice server on your own computer at `127.0.0.1`, an address that always means "this computer".
> Calling a real web API, as in the last section, needs an internet connection.

## How a web request works

A **client**, such as your program, sends a **request** to a **server**, which sends back a **response**.
The request names a **URL**: in `https://example.com/forecast?city=Oslo`, `https://example.com` is the server, `/forecast` is the **path**, and `?city=Oslo` is the **query string**.
Each request has an **HTTP method**: `GET` asks for data, and `POST` sends new data.

Each response has a **status code**:

- 200 to 299 mean success, such as `200 OK` and `201 Created`.
- 400 to 499 mean the request had a problem, such as `404 Not Found`.
- 500 to 599 mean the server had a problem, such as `503 Service Unavailable`.

A **web API** is a set of URLs that return data for programs, usually as JSON text.

## Make a GET request

```python
import requests

response = requests.get(
    "https://example.com/tides",
    params={"harbor": "North Bay"},
    timeout=5,
)
print(response.status_code)
data = response.json()
```

- `params` builds the query string, safely encoding spaces and symbols such as `&`.
- `timeout=5` gives up after 5 seconds; without a timeout, an unresponsive server can make the program wait forever.
- `response.json()` parses a JSON reply into dictionaries and lists.

## Decide what each status means

`requests.get()` raises an error only when no response arrives, such as `requests.ConnectionError` or `requests.Timeout`.
A 404 or 500 reply is still a response, so `get()` returns it normally.
`response.raise_for_status()` raises `requests.HTTPError` for a status of 400 or higher.
Handle statuses with a normal meaning first, then raise for the rest:

```python
if response.status_code == 404:
    return None
response.raise_for_status()
```

All of these errors are subclasses of `requests.RequestException`.

`requests.post(url, json=payload, timeout=5)` sends `payload` as a JSON body.
APIs often answer a successful POST with `201 Created` and a JSON description of the new record.

Respect rate limits, keep secret API keys out of your code, and expect real APIs to be slow or change.

## Try it in your own terminal

These steps need an internet connection and run outside Pytuitor.

1. In a virtual environment with requests installed, request `https://api.github.com/repos/python/cpython` with `timeout=10`.
2. Call `raise_for_status()`, then print `response.json()["stargazers_count"]`.
3. Change the URL to a repository that does not exist and observe the 404.
