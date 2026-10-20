# Store records in SQLite

A JSON or CSV file is rewritten as a whole.
A **database** lets a program add, find, and change individual records instead.
SQLite stores a database in a single file, and Python's standard `sqlite3` module uses it offline, with no server to install.

SQLite understands SQL, a language for working with records.
A **table** is a named collection of records; each record is a **row**, and each named value in a row is a **column**.

```python
import sqlite3

connection = sqlite3.connect("trail.db")
connection.execute("""
    CREATE TABLE IF NOT EXISTS sightings (
        animal TEXT PRIMARY KEY,
        count INTEGER NOT NULL
    )
""")
with connection:
    connection.execute("INSERT INTO sightings VALUES (?, ?)", ("owl", 2))
query = "SELECT animal, count FROM sightings ORDER BY animal"
rows = connection.execute(query).fetchall()
print(rows)
connection.close()
```

This prints `[('owl', 2)]`.

- `sqlite3.connect(path)` opens or creates the file; the path `":memory:"` creates a temporary database instead.
- `CREATE TABLE IF NOT EXISTS` creates the table only the first time; `PRIMARY KEY` makes each animal unique, and `NOT NULL` requires a value.
- `SELECT` chooses columns, `WHERE` filters rows, and `ORDER BY` sorts them.
- `fetchall()` returns a list of row tuples; `fetchone()` returns the next row, or `None` when none remain.

## Placeholders keep values out of SQL

Each `?` is a **placeholder**: `sqlite3` sends the values separately from the SQL text.
Never build SQL with f-strings or `+`.
A name such as `O'Brien` contains a quote that would end the SQL text early, and crafted input could change what the statement does, an attack called **SQL injection**.

## Transactions make changes permanent

A **transaction** groups changes so they are saved together or not at all.
Changes are saved only when the transaction is **committed**; without a commit, they disappear when the connection closes.
`with connection:` commits when its block succeeds and discards the block's changes if an exception occurs.
It does not close the connection, so still call `connection.close()`.

Inserting a row whose primary key already exists raises `sqlite3.IntegrityError`.
