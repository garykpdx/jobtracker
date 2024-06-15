from django.db import models
from django.contrib.auth.models import User

LOCATION_TYPE = {
    "ONSITE": "Onsite",
    "HYBRID": "Hybrid",
    "REMOTE": "Remote",
}
# Create your models here.
class JobApp(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    job_number = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=100)
    applied_dt = models.DateTimeField(auto_now_add=True)
    payrate = models.CharField(max_length=20, blank=True)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE)
    job_url = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=20, blank=True)
    contractor_name = models.CharField(max_length=100, blank=True)
    job_source = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f"{self.title}\t{self.company}"
