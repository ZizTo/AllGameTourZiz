from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.all_profiles_view),
    path("login/", views.loginView),
    path("logout/", views.logoutView),
    path('<str:usname>', views.profile_view)
]