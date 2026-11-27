from datetime import date, datetime, time, timedelta, timezone as dt_timezone
from types import SimpleNamespace
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.contrib.auth.models import AnonymousUser
from django.test import SimpleTestCase
from django.utils import timezone

from jobtracker import date_utils

TOKYO = ZoneInfo("Asia/Tokyo")
LA = ZoneInfo("America/Los_Angeles")
UTC = dt_timezone.utc


def freeze_now(dt):
    """Pin the 'current time' used by date_utils."""
    return patch("jobtracker.date_utils.timezone.now", return_value=dt)


def user_with_tz(value):
    return SimpleNamespace(profile=SimpleNamespace(timezone=value))


class GetUserTzTests(SimpleTestCase):
    def test_valid_timezone_string(self):
        self.assertEqual(date_utils.get_user_tz(user_with_tz("Asia/Tokyo")), TOKYO)

    def test_zoneinfo_object_is_accepted(self):
        # Timezone fields may hand back a ZoneInfo rather than a string.
        self.assertEqual(date_utils.get_user_tz(user_with_tz(TOKYO)), TOKYO)

    def test_no_profile_uses_default(self):
        user = SimpleNamespace()
        self.assertEqual(date_utils.get_user_tz(user), timezone.get_default_timezone())

    def test_profile_is_none_uses_default(self):
        user = SimpleNamespace(profile=None)
        self.assertEqual(date_utils.get_user_tz(user), timezone.get_default_timezone())

    def test_empty_timezone_uses_default(self):
        for empty in (None, ""):
            with self.subTest(value=empty):
                self.assertEqual(
                    date_utils.get_user_tz(user_with_tz(empty)),
                    timezone.get_default_timezone(),
                )

    def test_anonymous_user_uses_default(self):
        self.assertEqual(
            date_utils.get_user_tz(AnonymousUser()), timezone.get_default_timezone()
        )

    def test_invalid_timezone_falls_back_and_logs_warning(self):
        with self.assertLogs("jobtracker.date_utils", level="WARNING") as logs:
            result = date_utils.get_user_tz(user_with_tz("Not/AZone"))
        self.assertEqual(result, timezone.get_default_timezone())
        self.assertIn("Not/AZone", logs.output[0])


class LocalTodayTests(SimpleTestCase):
    # 03:00 UTC on Jan 1 is already Jan 1 in Tokyo but still Dec 31 in Los Angeles.
    NOW = datetime(2026, 1, 1, 3, 0, tzinfo=UTC)

    def test_ahead_of_utc(self):
        with freeze_now(self.NOW):
            self.assertEqual(date_utils.local_today(TOKYO), date(2026, 1, 1))

    def test_behind_utc(self):
        with freeze_now(self.NOW):
            self.assertEqual(date_utils.local_today(LA), date(2025, 12, 31))

    def test_utc(self):
        with freeze_now(self.NOW):
            self.assertEqual(date_utils.local_today(UTC), date(2026, 1, 1))

    def test_returns_a_date_not_datetime(self):
        with freeze_now(self.NOW):
            result = date_utils.local_today(UTC)
        self.assertNotIsInstance(result, datetime)


class DayRangeTests(SimpleTestCase):
    def test_single_day_covers_whole_day(self):
        start, end = date_utils.day_range(date(2026, 3, 5), date(2026, 3, 5), LA)
        self.assertEqual(start, datetime(2026, 3, 5, 0, 0, 0, 0, tzinfo=LA))
        self.assertEqual(end, datetime(2026, 3, 5, 23, 59, 59, 999999, tzinfo=LA))

    def test_multi_day_range(self):
        start, end = date_utils.day_range(date(2026, 3, 1), date(2026, 3, 31), UTC)
        self.assertEqual(start.date(), date(2026, 3, 1))
        self.assertEqual(start.time(), time.min)
        self.assertEqual(end.date(), date(2026, 3, 31))
        self.assertEqual(end.time(), time.max)

    def test_results_are_aware_and_use_given_tz(self):
        start, end = date_utils.day_range(date(2026, 3, 5), date(2026, 3, 5), TOKYO)
        for value in (start, end):
            self.assertIs(value.tzinfo, TOKYO)
            self.assertIsNotNone(value.utcoffset())

    def test_same_local_day_maps_to_different_utc_instants(self):
        tokyo_start, _ = date_utils.day_range(date(2026, 3, 5), date(2026, 3, 5), TOKYO)
        la_start, _ = date_utils.day_range(date(2026, 3, 5), date(2026, 3, 5), LA)
        self.assertNotEqual(tokyo_start, la_start)
        self.assertEqual(tokyo_start.astimezone(UTC), datetime(2026, 3, 4, 15, 0, tzinfo=UTC))

    def test_dst_spring_forward_day_has_both_offsets(self):
        # US clocks jump forward on 2026-03-08, so the day starts in PST and ends in PDT.
        start, end = date_utils.day_range(date(2026, 3, 8), date(2026, 3, 8), LA)
        self.assertEqual(start.utcoffset(), timedelta(hours=-8))
        self.assertEqual(end.utcoffset(), timedelta(hours=-7))

    def test_start_after_end_is_not_validated(self):
        # Documents current behavior: the function does not reorder or reject.
        start, end = date_utils.day_range(date(2026, 3, 10), date(2026, 3, 1), UTC)
        self.assertGreater(start, end)


class LastNDaysRangeTests(SimpleTestCase):
    NOW = datetime(2026, 10, 14, 18, 0, tzinfo=UTC)

    def test_default_is_30_days(self):
        with freeze_now(self.NOW):
            start, end = date_utils.last_n_days_range(UTC)
        self.assertEqual(start, datetime(2026, 9, 14, 0, 0, tzinfo=UTC))
        self.assertEqual(end, datetime(2026, 10, 14, 23, 59, 59, 999999, tzinfo=UTC))

    def test_custom_days(self):
        with freeze_now(self.NOW):
            start, end = date_utils.last_n_days_range(UTC, days=7)
        self.assertEqual(start.date(), date(2026, 10, 7))
        self.assertEqual(end.date(), date(2026, 10, 14))

    def test_zero_days_is_today_only(self):
        with freeze_now(self.NOW):
            start, end = date_utils.last_n_days_range(UTC, days=0)
        self.assertEqual(start.date(), end.date())

    def test_spans_n_plus_one_calendar_days(self):
        # Preserves existing behavior: "today minus 30" through end of today is 31 days.
        with freeze_now(self.NOW):
            start, end = date_utils.last_n_days_range(UTC, days=30)
        self.assertEqual((end.date() - start.date()).days + 1, 31)

    def test_uses_users_local_date(self):
        # 03:00 UTC Oct 15 is still Oct 14 in LA.
        now = datetime(2026, 10, 15, 3, 0, tzinfo=UTC)
        with freeze_now(now):
            _, end = date_utils.last_n_days_range(LA, days=30)
        self.assertEqual(end.date(), date(2026, 10, 14))
        self.assertIs(end.tzinfo, LA)

    def test_crosses_year_boundary(self):
        now = datetime(2026, 1, 10, 12, 0, tzinfo=UTC)
        with freeze_now(now):
            start, _ = date_utils.last_n_days_range(UTC, days=30)
        self.assertEqual(start.date(), date(2025, 12, 11))


class WeekBoundsTests(SimpleTestCase):
    def test_midweek_day(self):
        # 2026-10-14 is a Wednesday.
        start, end = date_utils.week_bounds(date(2026, 10, 14))
        self.assertEqual(start, date(2026, 10, 11))
        self.assertEqual(end, date(2026, 10, 17))

    def test_sunday_starts_its_own_week(self):
        start, end = date_utils.week_bounds(date(2026, 10, 11))
        self.assertEqual(start, date(2026, 10, 11))
        self.assertEqual(end, date(2026, 10, 17))

    def test_saturday_ends_its_week(self):
        start, end = date_utils.week_bounds(date(2026, 10, 17))
        self.assertEqual(start, date(2026, 10, 11))
        self.assertEqual(end, date(2026, 10, 17))

    def test_week_crossing_year_boundary(self):
        # 2026-01-01 is a Thursday; its week began on Sunday 2025-12-28.
        start, end = date_utils.week_bounds(date(2026, 1, 1))
        self.assertEqual(start, date(2025, 12, 28))
        self.assertEqual(end, date(2026, 1, 3))

    def test_every_day_of_a_year_gives_sunday_to_saturday(self):
        day = date(2026, 1, 1)
        for _ in range(366):
            with self.subTest(day=day):
                start, end = date_utils.week_bounds(day)
                self.assertEqual(start.isoweekday(), 7)  # Sunday
                self.assertEqual(end.isoweekday(), 6)  # Saturday
                self.assertLessEqual(start, day)
                self.assertGreaterEqual(end, day)
                self.assertEqual((end - start).days, 6)
            day += timedelta(days=1)


class WeekRangeTests(SimpleTestCase):
    def test_range_covers_full_week_in_tz(self):
        start, end = date_utils.week_range(date(2026, 10, 14), LA)
        self.assertEqual(start, datetime(2026, 10, 11, 0, 0, tzinfo=LA))
        self.assertEqual(end, datetime(2026, 10, 17, 23, 59, 59, 999999, tzinfo=LA))

    def test_matches_week_bounds_and_day_range(self):
        day = date(2026, 6, 3)
        expected = date_utils.day_range(*date_utils.week_bounds(day), TOKYO)
        self.assertEqual(date_utils.week_range(day, TOKYO), expected)


class RecentWeeksTests(SimpleTestCase):
    NOW = datetime(2026, 10, 14, 18, 0, tzinfo=UTC)  # a Wednesday

    def test_default_returns_four_weeks(self):
        with freeze_now(self.NOW):
            weeks = date_utils.recent_weeks(UTC)
        self.assertEqual(len(weeks), 4)

    def test_custom_count(self):
        for n in (1, 2, 8):
            with self.subTest(n=n), freeze_now(self.NOW):
                self.assertEqual(len(date_utils.recent_weeks(UTC, n=n)), n)

    def test_oldest_first_and_ends_with_current_week(self):
        with freeze_now(self.NOW):
            weeks = date_utils.recent_weeks(UTC, n=4)
        starts = [w[0] for w in weeks]
        self.assertEqual(
            starts,
            [date(2026, 9, 20), date(2026, 9, 27), date(2026, 10, 4), date(2026, 10, 11)],
        )
        self.assertEqual(weeks[-1][1], date(2026, 10, 17))

    def test_weeks_are_contiguous_and_sunday_aligned(self):
        with freeze_now(self.NOW):
            weeks = date_utils.recent_weeks(UTC, n=6)
        for week_start, week_end, _, _ in weeks:
            self.assertEqual(week_start.isoweekday(), 7)
            self.assertEqual((week_end - week_start).days, 6)
        for earlier, later in zip(weeks, weeks[1:]):
            self.assertEqual(later[0] - earlier[1], timedelta(days=1))

    def test_tuple_shape_and_ranges_match_dates(self):
        with freeze_now(self.NOW):
            weeks = date_utils.recent_weeks(LA, n=2)
        for week_start, week_end, range_start, range_end in weeks:
            self.assertEqual(range_start, datetime(week_start.year, week_start.month, week_start.day, tzinfo=LA))
            self.assertEqual(range_end.date(), week_end)
            self.assertEqual(range_end.time(), time.max)
            self.assertIs(range_start.tzinfo, LA)

    def test_current_week_depends_on_user_timezone(self):
        # 03:00 UTC Sunday Oct 18: already Sunday (new week) in Tokyo, still Saturday in LA.
        now = datetime(2026, 10, 18, 3, 0, tzinfo=UTC)
        with freeze_now(now):
            tokyo_current = date_utils.recent_weeks(TOKYO, n=1)[0][0]
            la_current = date_utils.recent_weeks(LA, n=1)[0][0]
        self.assertEqual(tokyo_current, date(2026, 10, 18))
        self.assertEqual(la_current, date(2026, 10, 11))

    def test_spans_year_boundary(self):
        now = datetime(2026, 1, 7, 12, 0, tzinfo=UTC)  # Wednesday
        with freeze_now(now):
            weeks = date_utils.recent_weeks(UTC, n=3)
        self.assertEqual([w[0] for w in weeks], [date(2025, 12, 21), date(2025, 12, 28), date(2026, 1, 4)])