from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
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
            form.save()
            return redirect("jobapps")
    else:
        form = RegisterUserForm()
    return render(request, "users/register.html", {"form": form})
