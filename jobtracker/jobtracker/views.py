import logging

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe

from jobapps.models import JobApp
from jobtracker.date_utils import (
    get_user_tz,
    last_n_days_range,
    local_today,
    recent_weeks,
    week_range,
)
from jobtracker.health import check_database

logger = logging.getLogger(__name__)


def homepage(request):
    logged_in = request.user.is_authenticated
    username = request.user.username

    user_tz = get_user_tz(request.user)
    today_local = local_today(user_tz)

    range_start, range_end = last_n_days_range(user_tz, days=30)
    week_range_start, week_range_end = week_range(today_local, user_tz)

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

    # Weekly counts for the last 4 weeks (including the current week), oldest to newest,
    # using the same Sunday-start week boundaries as jobcount_current_week above.
    try:
        weekly_counts = {}
        for w_start, w_end, w_range_start, w_range_end in recent_weeks(user_tz, n=4):
            week_count = (JobApp.objects.filter(user=request.user)
                          .filter(applied_dt__range=(w_range_start, w_range_end))
                          .count())

            label = f"{w_start.strftime('%b %d')} - {w_end.strftime('%b %d')}"
            weekly_counts[label] = week_count
    except Exception as e:
        print(e)
        weekly_counts = {}

    return render(request, 'home.html', {'jobcount_30_days': jobcount_30_days,
                                          'jobcount_current_week': jobcount_current_week,
                                          'daily_counts': count_by_date,
                                          'city_data': city_data,
                                          'weekly_counts': weekly_counts,
                                          'logged_in': logged_in, 'username': username})


@never_cache
@require_safe
def health(request):
    db_ok = check_database()
    return JsonResponse(
        {
            "status": "ok" if db_ok else "error",
            "database": "ok" if db_ok else "unavailable",
        },
        status=200 if db_ok else 503,
    )