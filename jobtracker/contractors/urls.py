from django.urls import path
from . import views

app_name = 'contractors'

urlpatterns = [
    path('', views.contractors_list, name='contractor_list'),
    path('details', views.contractor_page, name='contractor_page'),
]
