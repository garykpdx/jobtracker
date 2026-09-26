import csv

from django.utils import timezone

from .models import JobApp

# Guards against CSV injection: if a free-text field (company, title, etc.)
# starts with one of these characters, Excel/Sheets may interpret it as the
# start of a formula when the file is opened. Prefixing with a single quote
# forces it to be treated as plain text instead.
_FORMULA_PREFIXES = ("=", "+", "-", "@")


def _safe_cell(value):
    value = "" if value is None else str(value)
    if value and value[0] in _FORMULA_PREFIXES:
        return "'" + value
    return value


def write_jobapps_csv(output, user):
    """
    Write `user`'s job applications as CSV rows into `output` — any
    writable, file-like object (an HttpResponse works fine, since it
    supports .write()).
    """
    user_tz = getattr(getattr(user, "profile", None), "timezone", None) \
        or timezone.get_default_timezone()

    jobapps = JobApp.objects.filter(user=user).order_by("-applied_dt")

    writer = csv.writer(output)
    writer.writerow([
        "Applied Status",
        "Applied Date",
        "Job Title",
        "Company",
        "City",
        "Locality",
        "Payrate",
        "Location Type",
        "URL Link",
    ])

    for jobapp in jobapps:
        local_date = timezone.localtime(jobapp.applied_dt, timezone=user_tz).date()
        writer.writerow([
            _safe_cell(jobapp.job_status),
            local_date.isoformat(),
            _safe_cell(jobapp.title),
            _safe_cell(jobapp.company),
            _safe_cell(jobapp.city),
            _safe_cell(jobapp.locality),
            _safe_cell(jobapp.payrate),
            _safe_cell(jobapp.location_type),
            _safe_cell(jobapp.job_url),
        ])
