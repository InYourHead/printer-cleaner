from datetime import datetime

from printer_cleaner.cron import CronSchedule


def test_every_fifteen_minutes():
    schedule = CronSchedule.parse("*/15 * * * *")

    assert schedule.matches(datetime(2026, 5, 15, 10, 0))
    assert schedule.matches(datetime(2026, 5, 15, 10, 45))
    assert not schedule.matches(datetime(2026, 5, 15, 10, 46))


def test_next_after():
    schedule = CronSchedule.parse("30 2 * * 1")

    assert schedule.next_after(datetime(2026, 5, 15, 10, 0)) == datetime(2026, 5, 18, 2, 30)
