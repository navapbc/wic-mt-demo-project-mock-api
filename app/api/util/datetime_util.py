from datetime import date, datetime, time, timedelta, timezone

def utcnow() -> datetime:
    """Current time in UTC tagged with timezone info marking it as UTC, unlike datetime.utcnow().

    See https://docs.python.org/3/library/datetime.html#datetime.datetime.utcnow
    """
    return datetime.now(timezone.utc)
