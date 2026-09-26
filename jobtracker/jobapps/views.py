import logging
from datetime import datetime, time, timedelta, UTC

import bleach
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import (
    render,
    redirect,
)
from django.utils import timezone

from . import forms
from .exports import write_jobapps_csv
from .hashid_utils import decode_id, encode_id
from .models import (
    JobApp,
    JobComment,
    JOB_STATUS_TYPE,
)

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "b", "i", "u", "ul", "ol", "li", "a",
    "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "hr",
]
ALLOWED_ATTRS = {"a": ["href", "title", "target", "rel"]}

logger = logging.getLogger(__name__)


@login_required(login_url="/users/login/")
def jobapp_list(request):
    user = request.user
    user_tz = getattr(getattr(user, "profile", None), "timezone", None) \
              or timezone.get_default_timezone()

    now_local = timezone.localtime(timezone.now(), timezone=user_tz)
    today_local = now_local.date()
    start_date_local = today_local - timedelta(days=30)

    range_start = datetime.combine(start_date_local, time.min, tzinfo=user_tz)
    range_end = datetime.combine(today_local, time.max, tzinfo=user_tz)

    jobapps = (JobApp.objects.filter(user=user)
               .filter(applied_dt__range=(range_start, range_end))
               .filter(~Q(job_status__iexact="Closed"))
               .order_by("-created_dt"))
    return render(request, 'jobapps/jobapp_list.html', {"jobapps": jobapps})


@login_required(login_url="/users/login/")
def jobapp_page(request, job_hash):
    user = request.user
    job_id = decode_id(job_hash)
    if job_id is None:
        return redirect("jobapps")

    try:
        jobapp = JobApp.objects.filter(user=user).get(id=job_id)
    except JobApp.DoesNotExist:
        logger.warning("JobApp {} does not exist for user {}".format(job_id, user))
        return redirect("jobapps")

    if jobapp.user != user:
        logger.warning("JobApp {} is not owned by user {}".format(job_id, user))
        return redirect("jobapps")

    if request.method == "POST":
        job_status_update = request.POST.get("job_status_update", "").strip()
        if job_status_update:
            jobapp.job_status = job_status_update
            jobapp.save()

        comment_text = request.POST.get("comment_text", "").strip()
        if comment_text:
            JobComment.objects.create(
                user=user,
                jobapp=jobapp,
                text=comment_text,
                change_dt=timezone.now(),
            )

        delete_comment_id = request.POST.get("delete_comment_id")
        if delete_comment_id:
            JobComment.objects.filter(id=delete_comment_id, user=user, jobapp=jobapp).delete()

        return redirect("jobapp", job_hash=encode_id(jobapp.id))

    status_types = JOB_STATUS_TYPE.keys()
    job_comments = JobComment.objects.filter(user=user, jobapp=jobapp).order_by("-change_dt", "-id")

    return render(request, 'jobapps/jobapp_page.html',
                  {"jobapp": jobapp,
                   "status_types": status_types,
                   "job_comments": job_comments})


@login_required(login_url="/users/login/")
def new_jobapp(request):
    if request.method == "POST":
        form = forms.CreateJobapp(request.POST)
        if form.is_valid():
            # save with user
            jobapp = form.save(commit=False)
            jobapp.user = request.user
            jobapp.description = bleach.clean(jobapp.description, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
            jobapp.save()
            return redirect("jobapps")
    else:
        form = forms.CreateJobapp()
    return render(request, 'jobapps/new_jobapp.html', {"form": form})


@login_required(login_url="/users/login/")
def company_suggestions(request):
    """
    Returns up to 4 distinct company names this user has already applied to,
    matching the partial text they've typed so far. Used to warn the user
    they may be about to enter a duplicate application before they submit.
    """
    query = request.GET.get("q", "").strip()

    if len(query) < 3:
        return JsonResponse({"companies": []})

    companies = (JobApp.objects.filter(user=request.user, company__icontains=query)
    .order_by("company")
    .values_list("company", flat=True)
    .distinct()[:4])

    return JsonResponse({"companies": list(companies)})


@login_required(login_url="/users/login/")
def edit_jobapp(request, job_hash):
    user = request.user
    job_id = decode_id(job_hash)
    if job_id is None:
        return redirect("jobapps")

    try:
        jobapp = JobApp.objects.filter(user=user).get(id=job_id)
    except JobApp.DoesNotExist:
        return redirect("jobapps")
    if jobapp.user != user:
        return redirect("jobapps")
    form = forms.CreateJobapp(request.POST or None, instance=jobapp)
    if form.is_valid():
        jobapp.description = bleach.clean(jobapp.description, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
        form.save()
        return redirect("jobapp", job_hash=encode_id(job_id))
    status_types = JOB_STATUS_TYPE.keys()

    return render(request, 'jobapps/edit_jobapp.html', {"jobapp": jobapp, "form": form,
                                                        "status_types": status_types})


@login_required(login_url="/users/login/")
def delete_jobapp(request, job_hash):
    user = request.user
    job_id = decode_id(job_hash)
    if job_id is None:
        return redirect("jobapps")

    try:
        jobapp = JobApp.objects.filter(user=user).get(id=job_id)
    except JobApp.DoesNotExist:
        return redirect("jobapps")

    if jobapp.user != user:
        logger.warning("JobApp {} is not owned by user {}".format(job_id, user))
        return redirect("jobapps")

    if request.method == "POST":
        jobapp.delete()
        return redirect("jobapps")

    # If someone GETs this URL directly, just send them back to the detail page
    return redirect("jobapp", job_hash=encode_id(jobapp.id))


@login_required(login_url="/users/login/")
def search_job(request):
    if request.method == "POST":
        search_terms = request.POST.get("search_terms", "").strip()
        jobapps = (JobApp.objects.filter(user=request.user)
                   .filter(Q(description__icontains=search_terms)
                           | Q(company__icontains=search_terms)
                           | Q(job_id__icontains=search_terms))
                   .order_by("-created_dt"))
        count = len(jobapps)
        return render(request, 'jobapps/search_job.html',
                      {"jobapps": jobapps, "count": count, "search_terms": search_terms})

    return render(request, 'jobapps/search_job.html', {})


@login_required(login_url="/users/login/")
def export_jobapps_csv(request):
    user_tz = getattr(getattr(request.user, "profile", None), "timezone", None) \
        or timezone.get_default_timezone()
    date_str = timezone.localtime(timezone.now(), timezone=user_tz).strftime("%Y_%m_%d")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="job_applications_{date_str}.csv"'
    write_jobapps_csv(response, request.user)
    return response
