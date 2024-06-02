from django.shortcuts import render
from django.http import HttpResponse
from .models import JobApp

# Create your views here.
def jobapp_list(request):
    jobapps = JobApp.objects.all().order_by("-applied_dt")
    return render(request, 'jobapps/jobapp_list.html', {"jobapps": jobapps})


# should convert with int converter for using with job_id unique ID: <int:job_id>
def jobapp_page(request, slug):
    jobapp = JobApp.objects.get(slug=slug)
    return render(request, 'jobapps/jobapp_page.html', {"jobapp": jobapp})


def new_jobapp(request):
    return HttpResponse("New job app")
