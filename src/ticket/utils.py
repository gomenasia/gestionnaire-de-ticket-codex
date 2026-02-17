from datetime import datetime, time, timezone


def parse_deadline(value: str):
    if not value:
        return None

    try:
        parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None

    return datetime.combine(parsed_date, time.max, tzinfo=timezone.utc)


def to_utc_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def is_deadline_late(deadline: datetime, reference: datetime) -> bool:
    return to_utc_aware(deadline) < to_utc_aware(reference)


def format_countdown(deadline: datetime, reference: datetime) -> str:
    seconds_left = int((to_utc_aware(deadline) - to_utc_aware(reference)).total_seconds())
    days = abs(seconds_left) // 86400
    hours = (abs(seconds_left) % 86400) // 3600

    if seconds_left >= 0:
        return f"{days}j {hours}h restantes"
    return f"En retard de {days}j {hours}h"
