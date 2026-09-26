from django.urls import path
from . import views

urlpatterns = [
    path('', views.jobapp_list, name="jobapps"),
    path('new-job/', views.new_jobapp, name="new-job"),
    path('search/', views.search_job, name="search"),
    path('edit/<str:job_hash>', views.edit_jobapp, name="edit-job"),
    path('delete/<str:job_hash>/', views.delete_jobapp, name='delete-job'),
    path('company-suggestions/', views.company_suggestions, name='company-suggestions'),
    path("<str:job_hash>", views.jobapp_page, name="jobapp"),
    path("export/", views.export_jobapps_csv, name="export-jobapps"),
]
