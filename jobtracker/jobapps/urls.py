from django.urls import path
from . import views

urlpatterns = [
    path('', views.jobapp_list, name="jobapps"),
    path('new-job/', views.new_jobapp, name="new-job"),
    path('search/', views.search_job, name="search"),
    path('edit/<int:job_id>', views.edit_jobapp, name="edit-job"),
    path("<int:job_id>", views.jobapp_page, name="jobapp"),
]
