from datetime import date, timedelta

from django.db.models import Count
from django.shortcuts import render
from jobapps.models import JobApp


def homepage(request):
    logged_in = request.user.is_authenticated
    username = request.user.username
    today = date.today()
    start_date = today - timedelta(days=30)

    week_start = today - timedelta(days=(today.isoweekday() % 7))
    week_end = week_start + timedelta(days=6)

    try:
        jobcount_30_days = JobApp.objects.filter(applied_dt__range=(start_date, today)).filter(user=request.user).count()

        count_by_date = ((JobApp.objects.filter(user=request.user)
                          .filter(applied_dt__range=(start_date, today))
                          .values("applied_dt")
                          .annotate(date_count=Count("applied_dt")))
                         .order_by("-applied_dt"))
    except Exception as e:
        print(e)
        jobcount_30_days = 0
        count_by_date = []

    try:
        jobcount_current_week = JobApp.objects.filter(applied_dt__range=(week_start, week_end)).filter(user=request.user).count()
    except Exception as e:
        print(e)
        jobcount_current_week = 0

    try:
        city_counts = (JobApp.objects.filter(applied_dt__range=(week_start, week_end)).filter(user=request.user)
                        .values("city")
                        .annotate(count=Count("city"))
                        .order_by("-count"))
        city_data = {(entry["city"] or "Unknown"): entry["count"] for entry in city_counts}
    except Exception as e:
        print(e)
        city_data = {}

    return render(request, 'home.html', {'jobcount_30_days': jobcount_30_days,
                                          'jobcount_current_week': jobcount_current_week,
                                          'daily_counts': count_by_date,
                                          'city_data': city_data,
                                          'logged_in': logged_in, 'username': username})