import logging
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.utils import timezone

logger = logging.getLogger(__name__)


def get_user_tz(user):
    """User's profile timezone, or the project default if missing/invalid."""
    raw_tz = getattr(getattr(user, "profile", None), "timezone", None)
    if not raw_tz:
        return timezone.get_default_timezone()
    try:
        return ZoneInfo(str(raw_tz))
    except Exception as e:
        logger.warning("Failed to parse timezone %r: %s", raw_tz, e)
        return timezone.get_default_timezone()


def local_today(tz):
    return timezone.localtime(timezone.now(), timezone=tz).date()


def day_range(start_day, end_day, tz):
    """Aware datetimes from the start of start_day to the end of end_day."""
    return (datetime.combine(start_day, time.min, tzinfo=tz),
            datetime.combine(end_day, time.max, tzinfo=tz))


def last_n_days_range(tz, days=30):
    today = local_today(tz)
    return day_range(today - timedelta(days=days), today, tz)


def week_bounds(day):
    """Sunday-Saturday dates of the week containing `day`."""
    start = day - timedelta(days=day.isoweekday() % 7)
    return start, start + timedelta(days=6)


def week_range(day, tz):
    start, end = week_bounds(day)
    return day_range(start, end, tz)


def recent_weeks(tz, n=4):
    """(week_start, week_end, range_start, range_end) for the last n weeks, oldest first."""
    this_start, _ = week_bounds(local_today(tz))
    result = []
    for weeks_ago in range(n - 1, -1, -1):
        start = this_start - timedelta(weeks=weeks_ago)
        end = start + timedelta(days=6)
        result.append((start, end, *day_range(start, end, tz)))
    return result