from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path('profile/', views.profile_view, name="profile"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path("set-timezone/", views.set_detected_timezone, name="set-timezone"),
]
