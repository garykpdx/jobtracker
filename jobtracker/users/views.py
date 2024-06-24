from django.shortcuts import render, redirect
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
)
from django.contrib.auth.models import User
from django.contrib.auth import (
    login,
    logout,
)
from django import forms


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=75)

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")


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


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
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