from django import forms
from . import models


class CreateJobapp(forms.ModelForm):
    class Meta:
        model = models.JobApp
        fields = [
            "title",
            "description",
            "job_number",
            "company",
            "city",
            "state",
            "payrate",
            "location_type",
            "contractor_name",
            "job_url",
            "job_source",
        ]
