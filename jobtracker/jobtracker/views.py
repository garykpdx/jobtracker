from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone as django_timezone

from jobapps.models import JobApp


def homepage(request):
    logged_in = request.user.is_authenticated
    username = request.user.username

    raw_tz = getattr(getattr(request.user, "profile", None), "timezone", None)
    try:
        user_tz = ZoneInfo(str(raw_tz)) if raw_tz else django_timezone.get_default_timezone()
    except Exception as e:
        print(e)
        user_tz = django_timezone.get_default_timezone()

    now_local = django_timezone.localtime(django_timezone.now(), timezone=user_tz)
    today_local = now_local.date()
    start_date_local = today_local - timedelta(days=30)

    week_start_local = today_local - timedelta(days=(today_local.isoweekday() % 7))
    week_end_local = week_start_local + timedelta(days=6)

    range_start = datetime.combine(start_date_local, time.min, tzinfo=user_tz)
    range_end = datetime.combine(today_local, time.max, tzinfo=user_tz)

    week_range_start = datetime.combine(week_start_local, time.min, tzinfo=user_tz)
    week_range_end = datetime.combine(week_end_local, time.max, tzinfo=user_tz)

    try:
        jobcount_30_days = (JobApp.objects.filter(user=request.user)
                             .filter(applied_dt__range=(range_start, range_end))
                             .count())
    except Exception as e:
        print(e)
        jobcount_30_days = 0

    try:
        count_by_date = list(JobApp.objects.filter(user=request.user)
                              .filter(applied_dt__range=(range_start, range_end))
                              .annotate(local_date=TruncDate("applied_dt", tzinfo=user_tz))
                              .values("local_date")
                              .annotate(date_count=Count("id"))
                              .order_by("-local_date"))
    except Exception as e:
        print(repr(e))
        print(repr(e.__cause__))
        count_by_date = []

    try:
        jobcount_current_week = (JobApp.objects.filter(user=request.user)
                                  .filter(applied_dt__range=(week_range_start, week_range_end))
                                  .count())
    except Exception as e:
        print(e)
        jobcount_current_week = 0

    try:
        city_counts = list(JobApp.objects.filter(user=request.user)
                            .filter(applied_dt__range=(week_range_start, week_range_end))
                            .values("locality")
                            .annotate(count=Count("locality"))
                            .order_by("-count"))
        city_data = {(entry["locality"] or "Unknown"): entry["count"] for entry in city_counts}
    except Exception as e:
        print(e)
        city_data = {}

    return render(request, 'home.html', {'jobcount_30_days': jobcount_30_days,
                                          'jobcount_current_week': jobcount_current_week,
                                          'daily_counts': count_by_date,
                                          'city_data': city_data,
                                          'logged_in': logged_in, 'username': username})
