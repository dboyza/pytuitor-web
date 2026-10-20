## Calendar dates and clock times

A `date` identifies a calendar day, a `time` identifies a clock reading, and a `datetime` combines both.
`datetime.strptime(text, format)` reads text using a format string that describes where the date and time parts appear.
`strftime(format)` formats an existing value as text.

```python
from datetime import datetime, timedelta

start = datetime.strptime("2024-07-08 14:30", "%Y-%m-%d %H:%M")
finish = start + timedelta(minutes=45)
print(finish.strftime("%d/%m/%Y %H:%M"))
```

The output is `08/07/2024 15:15`.
`%Y` means four-digit year, `%m` month, `%d` day, `%H` hour in a 24-hour clock, and `%M` minute.
Uppercase and lowercase format letters have different meanings.
Invalid dates or incompatible text raise `ValueError`.

A datetime's `.date()` and `.time()` methods return just its date or time part.
`datetime.combine(day, clock)` joins a date and time into one datetime.
Do arithmetic on the combined datetime so crossing midnight preserves the new day.
These examples use calendar dates and clock readings without time-zone information.
They do not account for clocks changing for daylight saving or compare times in different time zones.
