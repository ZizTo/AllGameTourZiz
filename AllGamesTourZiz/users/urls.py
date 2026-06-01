from django.urls import path, include
from . import views

urlpatterns = [
    path("login/", views.loginView),
    path("logout/", views.logoutView)
]