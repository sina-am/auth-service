from datetime import datetime, date


def date_to_datetime(d: date) -> datetime:
    return datetime.fromisoformat(d.isoformat())
