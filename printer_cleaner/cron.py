from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class CronSchedule:
    minutes: set[int]
    hours: set[int]
    days_of_month: set[int]
    months: set[int]
    days_of_week: set[int]

    @classmethod
    def parse(cls, expression: str) -> "CronSchedule":
        parts = expression.split()
        if len(parts) != 5:
            raise ValueError("CRON_SCHEDULE must use 5 fields: minute hour day-of-month month day-of-week")

        return cls(
            minutes=_parse_field(parts[0], 0, 59),
            hours=_parse_field(parts[1], 0, 23),
            days_of_month=_parse_field(parts[2], 1, 31),
            months=_parse_field(parts[3], 1, 12),
            days_of_week=_parse_field(parts[4], 0, 6),
        )

    def matches(self, value: datetime) -> bool:
        cron_day = (value.weekday() + 1) % 7
        return (
            value.minute in self.minutes
            and value.hour in self.hours
            and value.day in self.days_of_month
            and value.month in self.months
            and cron_day in self.days_of_week
        )

    def next_after(self, value: datetime) -> datetime:
        candidate = value.replace(second=0, microsecond=0) + timedelta(minutes=1)
        limit = candidate + timedelta(days=366)
        while candidate <= limit:
            if self.matches(candidate):
                return candidate
            candidate += timedelta(minutes=1)
        raise ValueError("Could not find a matching cron time within one year")


def _parse_field(field: str, minimum: int, maximum: int) -> set[int]:
    values: set[int] = set()
    for item in field.split(","):
        values.update(_parse_item(item.strip(), minimum, maximum))
    if not values:
        raise ValueError(f"Empty cron field: {field}")
    return values


def _parse_item(item: str, minimum: int, maximum: int) -> set[int]:
    if not item:
        raise ValueError("Empty cron item")

    if "/" in item:
        base, step_text = item.split("/", 1)
        step = int(step_text)
        if step <= 0:
            raise ValueError("Cron step must be greater than 0")
    else:
        base = item
        step = 1

    if base == "*":
        start, end = minimum, maximum
    elif "-" in base:
        start_text, end_text = base.split("-", 1)
        start, end = int(start_text), int(end_text)
    else:
        start = end = int(base)

    if start < minimum or end > maximum or start > end:
        raise ValueError(f"Cron value out of range: {item}")

    return set(range(start, end + 1, step))
