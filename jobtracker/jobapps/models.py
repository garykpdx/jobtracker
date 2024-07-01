from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

LOCATION_TYPE = {
    "Onsite": "Onsite",
    "Hybrid": "Hybrid",
    "Remote": "Remote",
}

JOB_STATUS_TYPE = {
    "Applied": "Applied",
    "Qualified": "Qualified",
    "Interviewed": "Interviewed",
    "Closed": "Closed",
    "Offered": "Offered",
}


class JobApp(models.Model):
    title = models.CharField(max_length=255)
    job_status = models.CharField(max_length=15, default="APPLIED", choices=JOB_STATUS_TYPE)
    description = models.TextField()
    job_number = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=100)
    applied_dt = models.DateField(auto_now_add=True)
    payrate = models.CharField(max_length=20, blank=True)
    location_type = models.CharField(max_length=10, choices=LOCATION_TYPE)
    job_url = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=20, blank=True)
    contractor_name = models.CharField(max_length=100, blank=True)
    job_source = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    created_dt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}\t{self.company}"
