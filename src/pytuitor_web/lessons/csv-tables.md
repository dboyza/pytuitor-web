## Rows and columns in a text file
CSV stands for comma-separated values.
It stores a table as rows of values, with each value called a field.
A header row names the columns.
A field can contain a comma if it is quoted, so splitting each line at commas can produce the wrong columns.
Parsing means reading text according to its format and turning it into values a program can use.
Python's `csv` module handles those details.

```python
import csv

with open("stock.csv", newline="", encoding="utf-8") as handle:
    for row in csv.DictReader(handle):
        print(row["item"], int(row["count"]))
```

`DictReader` uses the first row as column names and returns one dictionary for each remaining row.
Every field starts as a string, even when it contains digits.
`newline=""` lets the CSV module handle line endings correctly.
