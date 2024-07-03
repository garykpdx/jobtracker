from django.shortcuts import (
    render,
    redirect,
)
from django.contrib.auth.decorators import login_required
from .models import Contractor
from . import forms

# Create your views here.

@login_required(login_url="/users/login/")
def contractors_list(request):
    user = request.user
    contractors = (Contractor.objects.filter(app_user=user).order_by("company"))
    return render(request, 'contractors/contractor_list.html', {"contractors": contractors})


@login_required(login_url="/users/login/")
def contractor_page(request):
    user = request.user

    return render(request, 'contractors/contractor_page.html', {})

@login_required(login_url="/users/login/")
def new_contractor(request):
    if request.method == "POST":
        form = forms.ContractorForm(request.POST)
        if form.is_valid():
            # save with user
            contractor = form.save(commit=False)
            contractor.user = request.user
            contractor.save()
            return redirect("details")
    else:
        form = forms.ContractorForm()
    return render(request, 'contractors/new_contractor.html', {"form": form})
