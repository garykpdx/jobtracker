from datetime import date, timedelta

from django.db.models import Count
from django.shortcuts import render
from jobapps.models import JobApp


def homepage(request):
    today = date.today()
    start_date = today - timedelta(days=30)
    jobcount = JobApp.objects.filter(applied_dt__range=(start_date, today)).filter(user=request.user).count()

    count_by_date = ((JobApp.objects.filter(user=request.user)
                      .filter(applied_dt__range=(start_date, today))
                      .values("applied_dt")
                      .annotate(date_count=Count("applied_dt")))
                     .order_by("-applied_dt"))

    return render(request, 'home.html', {'jobcount': jobcount, 'daily_counts': count_by_date})
