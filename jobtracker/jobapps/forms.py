from django import forms
from . import models


class CreateJobapp(forms.ModelForm):
    required_css_class = "required"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].required = True
        self.fields["title"].required = True
        self.fields["job_status"].required = True
        self.fields["job_url"].required = False
        self.fields["description"].required = True
        self.fields["job_id"].required = False
        self.fields["city"].required = False
        self.fields["state"].required = False
        self.fields["locality"].required = False
        self.fields["payrate"].required = False
        self.fields["location_type"].required = True
        self.fields["contractor_name"].required = False
        self.fields["job_source"].required = False

    class Meta:
        model = models.JobApp
        fields = [
            "company",
            "title",
            "job_status",
            "description",
            "job_id",
            "city",
            "state",
            "locality",
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
            "description": forms.Textarea(attrs={"class": "form-control",
                                                 "title": "Freeform HTML text",
                                                 "data-bs-toggle": "tooltip",
                                                 "data-bs-placement": "top"
                                                 }),
            "job_id": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "locality": forms.TextInput(attrs={"class": "form-control",
                                               "title": "Location as you define it (e.g. metro area, state, country)",
                                               "data-bs-toggle": "tooltip",
                                               "data-bs-placement": "top"}),
            "payrate": forms.TextInput(attrs={"class": "form-control"}),
            "location_type": forms.Select(attrs={"class": "form-control form-select"}),
            "contractor_name": forms.TextInput(attrs={"class": "form-control"}),
            "job_url": forms.TextInput(attrs={"class": "form-control", "placeholder": "http://"}),
            "job_source": forms.TextInput(attrs={"class": "form-control",
                                                 "title": "Where you found the job",
                                                 "data-bs-toggle": "tooltip",
                                                 "data-bs-placement": "top"}),
        }
