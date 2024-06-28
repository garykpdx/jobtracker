from django import forms
from . import models


class CreateJobapp(forms.ModelForm):
    class Meta:
        model = models.JobApp
        fields = [
            "company",
            "title",
            "job_status",
            "description",
            "job_number",
            "city",
            "state",
            "payrate",
            "location_type",
            "contractor_name",
            "job_url",
            "job_source",
        ]

        widgets = {
            "company": forms.TextInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "job_status": forms.Select(attrs={"class": "form-control form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "job_number": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "payrate": forms.TextInput(attrs={"class": "form-control"}),
            "location_type": forms.Select(attrs={"class": "form-control form-select"}),
            "contractor_name": forms.TextInput(attrs={"class": "form-control"}),
            "job_url": forms.TextInput(attrs={"class": "form-control", "placeholder": "http://"}),
            "job_source": forms.TextInput(attrs={"class": "form-control"}),
        }
