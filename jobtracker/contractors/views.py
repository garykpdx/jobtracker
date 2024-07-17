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
def contractor_page(request, contractor_id):
    user = request.user
    try:
        contractor = Contractor.objects.filter(app_user=user).get(id=contractor_id)
    except Contractor.DoesNotExist:
        return redirect("contractors:contractor_list")

    if contractor.app_user != user:
        return redirect("contractors:contractor_list")

    return render(request, 'contractors/contractor_page.html', {"contractor": contractor})


@login_required(login_url="/users/login/")
def edit_contractor(request, contractor_id):
    user = request.user
    try:
        contractor = Contractor.objects.filter(app_user=user).get(id=contractor_id)
    except Contractor.DoesNotExist:
        return redirect("contractors:contractor_list")
    # if contractor.app_user != user:
    #     return redirect("contractors:contractor_list")

    form = forms.ContractorForm(request.POST or None, instance=contractor)
    if form.is_valid():
        form.save()
        return redirect("contractors:contractor_page", contractor_id=contractor_id)

    return render(request, 'contractors/edit_contractor.html', {"contractor": contractor,
                                                                "form": form, "username": user})


@login_required(login_url="/users/login/")
def new_contractor(request):
    if request.method == "POST":
        form = forms.ContractorForm(request.POST)
        if form.is_valid():
            # save with user
            contractor = form.save(commit=False)
            contractor.app_user = request.user
            contractor.save()
            return redirect("contractors:contractor_page", contractor_id=contractor.id)
    else:
        form = forms.ContractorForm()
    return render(request, 'contractors/new_contractor.html', {"form": form})
