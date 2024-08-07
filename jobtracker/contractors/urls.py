from django.urls import path
from . import views

app_name = 'contractors'

urlpatterns = [
    path('', views.contractors_list, name='contractor_list'),
    path('contractor_page/<int:contractor_id>', views.contractor_page, name='contractor_page'),
    path('edit_contractor/<int:contractor_id>', views.edit_contractor, name='edit_contractor'),
    path('new_contractor', views.new_contractor, name='new_contractor'),
]
