from django.db import models

# Create your models here.
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User


class Contractor(models.Model):
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=100, blank=True)
    app_user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    created_dt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}\t{self.company}"
