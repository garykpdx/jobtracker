from django.urls import path
from . import views

urlpatterns = [
    path('', views.jobapp_list, name="jobapps"),
    path('new-job/', views.new_jobapp, name="newjob"),
    path("<slug:slug>", views.jobapp_page, name="jobapp"),
]
