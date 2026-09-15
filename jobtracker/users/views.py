from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from zoneinfo import available_timezones
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
)
from django.contrib.auth.models import User
from django.contrib.auth import (
    login,
    logout,
)
from django import forms

from users.forms import EditProfileForm, ProfileSettingsForm
from users.models import UserProfile

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=75)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")


class UpdateUserForm(UserChangeForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=75)
    last_name = forms.CharField(max_length=75)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")


# Create your views here.
def register_view(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            login(request, form.save())
            return redirect("jobapps")
    else:
        if request.user.is_superuser:
            form = RegisterUserForm()
        else:
            return redirect("jobapps")
    return render(request, "users/register.html", {"form": form})


def profile_view(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)
        profile_form = ProfileSettingsForm(request.POST, instance=user_profile)
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
    else:
        form = EditProfileForm(instance=request.user)
        profile_form = ProfileSettingsForm(instance=user_profile)

    return render(request, "users/user_profile.html", {
        "form": form,
        "profile_form": profile_form,
    })


@login_required
@require_POST
def set_detected_timezone(request):
    """
    Auto-set the user's timezone from the browser, but only the first
    time — never overwrite a timezone the user has already chosen
    (whether that came from a previous auto-detect or a manual pick).
    """
    tz_name = request.POST.get("timezone")
    if not tz_name or tz_name not in available_timezones():
        return HttpResponseBadRequest("Invalid timezone")

    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not user_profile.timezone:
        user_profile.timezone = tz_name
        user_profile.save(update_fields=["timezone"])

    return JsonResponse({"timezone": str(user_profile.timezone)})



def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if "next" in request.POST:
                return redirect(request.POST.get("next"))
            return redirect("jobapps")
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return render(request, "users/login.html")