import logging

from django.shortcuts import render, redirect
from django.contrib import messages
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
    update_session_auth_hash,
)
from django import forms

from users.forms import EditProfileForm, ProfileSettingsForm, CustomPasswordChangeForm
from users.models import UserProfile

logger = logging.getLogger(__name__)


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


@login_required(login_url="/users/login/")
def register_view(request):
    # This check must run for every request method. Previously it only ran
    # in the GET branch below, which meant a POST straight to this URL —
    # from any logged-in non-admin, or even logged out entirely — could
    # create an account with no admin check at all.
    if not request.user.is_superuser:
        logger.warning(
            "Non-superuser attempted to access registration: user=%s method=%s",
            request.user.username,
            request.method,
        )
        messages.error(request, "You do not have permission to register new users.")
        return redirect("jobapps")

    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            try:
                new_user = form.save()
            except Exception:
                # Catches anything unexpected (DB error, etc.) beyond normal
                # form validation, so the admin isn't left looking at a 500
                # page with no explanation.
                logger.exception(
                    "Unexpected error creating user username=%s (requested by admin=%s)",
                    request.POST.get("username"),
                    request.user.username,
                )
                messages.error(
                    request,
                    "Something went wrong while creating this user. "
                    "The error has been logged; please try again or check the logs.",
                )
                return render(request, "users/register.html", {"form": form})

            # Deliberately NOT calling login() here — this form is used by an
            # admin to create an account for someone else. Logging the new
            # user in would end the admin's own session.
            logger.info(
                "New user registered: %s (created by admin=%s)",
                new_user.username,
                request.user.username,
            )
            messages.success(request, f"User \"{new_user.username}\" was registered successfully.")
            return redirect("users:register")
        else:
            logger.warning(
                "Registration form invalid (submitted by admin=%s) for username=%s errors=%s",
                request.user.username,
                request.POST.get("username"),
                form.errors.as_json(),
            )
            messages.error(request, "Registration failed — please correct the errors below.")
    else:
        form = RegisterUserForm()

    return render(request, "users/register.html", {"form": form})


@login_required
def profile_view(request):
    """Read-only display of the current user's profile."""
    UserProfile.objects.get_or_create(user=request.user)
    return render(request, "users/user_profile.html")


@login_required
def profile_edit(request):
    """Edit form for the current user's profile, plus a separate password-change form."""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if created:
        logger.info("Created new UserProfile for user=%s", request.user.username)

    if request.method == "POST" and "profile_submit" in request.POST:
        form = EditProfileForm(request.POST, instance=request.user)
        profile_form = ProfileSettingsForm(request.POST, instance=user_profile)
        password_form = CustomPasswordChangeForm(user=request.user)

        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            logger.info("Profile updated for user=%s", request.user.username)
            return redirect("users:profile")
        else:
            logger.warning(
                "Profile update failed for user=%s form_errors=%s profile_errors=%s",
                request.user.username,
                form.errors.as_json(),
                profile_form.errors.as_json(),
            )

    elif request.method == "POST" and "password_submit" in request.POST:
        form = EditProfileForm(instance=request.user)
        profile_form = ProfileSettingsForm(instance=user_profile)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if password_form.is_valid():
            updated_user = password_form.save()
            # Keeps the user logged in after their password hash changes,
            # instead of the session being invalidated mid-request.
            update_session_auth_hash(request, updated_user)
            logger.info("Password changed for user=%s", request.user.username)
            return redirect("users:profile")
        else:
            logger.warning(
                "Password change failed for user=%s errors=%s",
                request.user.username,
                password_form.errors.as_json(),
            )

    else:
        form = EditProfileForm(instance=request.user)
        profile_form = ProfileSettingsForm(instance=user_profile)
        password_form = CustomPasswordChangeForm(user=request.user)

    return render(request, "users/edit_user_profile.html", {
        "form": form,
        "profile_form": profile_form,
        "password_form": password_form,
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
        logger.warning(
            "Invalid timezone submitted by user=%s timezone=%r",
            request.user.username,
            tz_name,
        )
        return HttpResponseBadRequest("Invalid timezone")

    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not user_profile.timezone:
        user_profile.timezone = tz_name
        user_profile.save(update_fields=["timezone"])
        logger.info("Auto-detected timezone set for user=%s timezone=%s", request.user.username, tz_name)

    return JsonResponse({"timezone": str(user_profile.timezone)})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            logger.info("User logged in: %s", form.get_user().username)
            if "next" in request.POST:
                logger.info("Redirecting to next URL: %s", request.POST.get("next"))
                return redirect(request.POST.get("next"))
            return redirect("jobapps")
        else:
            logger.warning(
                "Failed login attempt for username=%s password_length=%d errors=%s",
                request.POST.get("username"),
                len(request.POST.get("password", "")),
                form.errors.as_json(),
            )
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        username = request.user.username if request.user.is_authenticated else "anonymous"
        logout(request)
        logger.info("User logged out: %s", username)
    return redirect("users:login")
