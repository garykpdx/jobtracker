from django import forms
from . import models


class CreateJobApp(forms.ModelForm):
    class Meta:
        model = models.JobApp
        fields = [
            'title',
            'description',
            'job_number',
            'company',
            'payrate',
            'location_type',
            'job_url',
            'city',
            'state',
            'contractor_name',
            'job_source',
            'slug',
        ]
