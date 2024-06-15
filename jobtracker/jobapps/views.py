from django.shortcuts import (
    render,
    redirect,
)
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import JobApp
from . import forms


# Create your views here.
@login_required(login_url="/users/login/")
def jobapp_list(request):
    jobapps = JobApp.objects.all().order_by("-applied_dt")
    return render(request, 'jobapps/jobapp_list.html', {"jobapps": jobapps})


# should convert with int converter for using with job_id unique ID: <int:job_id>
@login_required(login_url="/users/login/")
def jobapp_page(request, slug):
    jobapp = JobApp.objects.get(slug=slug)
    return render(request, 'jobapps/jobapp_page.html', {"jobapp": jobapp})


@login_required(login_url="/users/login/")
def new_jobapp(request):
    if request.method == "POST":
        form = forms.CreateJobapp(request.POST)
        if form.is_valid():
            # save with user
            jobapp = form.save(commit=False)
            jobapp.user = request.user
            jobapp.save()
            return redirect("jobapps")
    else:
        form = forms.CreateJobapp()
    return render(request, 'jobapps/new_jobapp.html', {"form": form})
