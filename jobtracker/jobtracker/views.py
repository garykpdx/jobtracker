from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from jobapps.models import JobApp

def homepage(request):
    # return HttpResponse("Hello world")
    jobcount = JobApp.objects.count()
    count_by_date = ((JobApp.objects.filter(user=request.user)
                     .values("applied_dt")
                     .annotate(date_count=Count("applied_dt")))
                     .order_by("-applied_dt"))

    return render(request, 'home.html', {'jobcount':jobcount, 'daily_counts': count_by_date})
