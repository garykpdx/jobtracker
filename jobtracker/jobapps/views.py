from datetime import date, timedelta

from django.db.models import Q
from django.shortcuts import (
    render,
    redirect,
)
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import JobApp, JOB_STATUS_TYPE
from . import forms


# Create your views here.
@login_required(login_url="/users/login/")
def jobapp_list(request):
    user = request.user
    today = date.today()
    start_date = today - timedelta(days=30)
    jobapps = (JobApp.objects
               .filter(user=user)
               .filter(applied_dt__range=(start_date, today))
               .filter(~Q(job_status="CLOSED"))
               .order_by("-created_dt"))
    return render(request, 'jobapps/jobapp_list.html', {"jobapps": jobapps})


# should convert with int converter for using with job_id unique ID: <int:job_id>
@login_required(login_url="/users/login/")
def jobapp_page(request, job_id):
    user = request.user
    try:
        jobapp = JobApp.objects.filter(user=user).get(id=job_id)
    except JobApp.DoesNotExist:
        return redirect("jobapps")
    if jobapp.user != user:
        return redirect("jobapps")
    status_types = JOB_STATUS_TYPE.keys()
    job_status_update = request.POST.get("job_status_update")
    if job_status_update:
        jobapp.job_status = job_status_update
        jobapp.save()
    return render(request, 'jobapps/jobapp_page.html', {"jobapp": jobapp, "status_types": status_types})


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


@login_required(login_url="/users/login/")
def edit_jobapp(request, job_id):
    user = request.user
    try:
        jobapp = JobApp.objects.filter(user=user).get(id=job_id)
    except JobApp.DoesNotExist:
        return redirect("jobapps")
    if jobapp.user != user:
        return redirect("jobapps")
    form = forms.CreateJobapp(request.POST or None, instance=jobapp)
    if form.is_valid():
        form.save()
        return redirect("jobapp", job_id=job_id)
    status_types = JOB_STATUS_TYPE.keys()

    return render(request, 'jobapps/edit_jobapp.html', {"jobapp": jobapp, "form": form,
                                                        "status_types": status_types})


@login_required(login_url="/users/login/")
def search_job(request):
    if request.method == "POST":
        search_terms = request.POST["search_terms"]
        jobapps = (JobApp.objects.filter(Q(description__contains=search_terms)
                                         | Q(company__contains=search_terms)
                                         | Q(job_number__contains=search_terms))
                   .order_by("-created_dt"))
        count = len(jobapps)
        return render(request, 'jobapps/search_job.html',
                      {"jobapps": jobapps, "count": count, "search_terms": search_terms})

    return render(request, 'jobapps/search_job.html', {})
