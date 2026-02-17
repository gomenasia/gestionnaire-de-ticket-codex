from datetime import datetime, time, timezone


def parse_deadline(value: str):
    if not value:
        return None

    try:
        parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None

    return datetime.combine(parsed_date, time.max, tzinfo=timezone.utc)


def format_countdown(deadline: datetime, reference: datetime) -> str:
    seconds_left = int((deadline - reference).total_seconds())
    days = abs(seconds_left) // 86400
    hours = (abs(seconds_left) % 86400) // 3600

    if seconds_left >= 0:
        return f"{days}j {hours}h restantes"
    return f"En retard de {days}j {hours}h"