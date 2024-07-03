from django import forms
from . import models

# name = models.CharField(max_length=255)
# company = models.CharField(max_length=100)
# phone = models.CharField(max_length=20)
# email = models.CharField(max_length=100)
# app_user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

class ContractorForm(forms.ModelForm):
    class Meta:
        model = models.JobApp
        fields = [
            "name",
            "company",
            "phone",
            "email",
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "company": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.Select(attrs={"class": "form-control form-select"}),
            "email": forms.Textarea(attrs={"class": "form-control"}),
        }
