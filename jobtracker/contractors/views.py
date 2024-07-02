from django.shortcuts import (
    render,
    redirect,
)
from django.contrib.auth.decorators import login_required
from .models import Contractor

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
