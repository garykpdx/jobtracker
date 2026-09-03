from django import forms
from django.contrib.auth.models import User

from .models import UserProfile


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
        ]

        widgets = {
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }


class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["timezone"]

        widgets = {
            "timezone": forms.Select(attrs={"class": "form-control form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["timezone"].required = True