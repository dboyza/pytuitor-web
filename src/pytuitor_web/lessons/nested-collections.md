## Lists can contain other lists

A grid can be represented as a list of rows, each itself a list.
Rows do not have to have equal lengths.

```python
grid = [[4, 7], [], [2]]
print(grid[0][1])
```

`grid[0]` selects the first row; its item at index `1` is `7`.
Indexing an empty row raises `IndexError`, just like indexing an empty ordinary list.
A **nested loop** is a loop inside another loop.
The outer loop below visits each row; the inner loop visits the values in that row.
`print()` can take several arguments separated by commas; it displays them with spaces between them:

```python
for row_number, row in enumerate(grid):
    for column_number, value in enumerate(row):
        print(row_number, column_number, value)
```

The inner loop finishes before the outer loop advances to another row.
An empty row runs the inner loop zero times.
Create a new row list for each row.
If you add the same list more than once, changing it later changes what you see at each of those positions.
