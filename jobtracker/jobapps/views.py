from django.shortcuts import render
from django.http import HttpResponse
from .models import JobApp
from . import forms


# Create your views here.
def jobapp_list(request):
    jobapps = JobApp.objects.all().order_by("-applied_dt")
    return render(request, 'jobapps/jobapp_list.html', {"jobapps": jobapps})


# should convert with int converter for using with job_id unique ID: <int:job_id>
def jobapp_page(request, slug):
    jobapp = JobApp.objects.get(slug=slug)
    return render(request, 'jobapps/jobapp_page.html', {"jobapp": jobapp})


# @login_required(login_url="users/login/")
def new_jobapp(request):
    form = forms.CreateJobApp()
    return render(request, "jobapps/jobapp_new.html", {"form": form})
