from django.db import models


# Create your models here.
class JobApp(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    job_number = models.CharField(max_length=30)
    company = models.CharField(max_length=100)
    applied_dt = models.DateTimeField(auto_now_add=True)
    payrate = models.CharField(max_length=20)
    location_type = models.CharField(max_length=20)
    job_url = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=20)
    contractor_name = models.CharField(max_length=100)
    job_source = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.title}\t{self.company}"
