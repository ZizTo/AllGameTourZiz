from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.all_sessions_view),
    path('<str:sessionid>', views.session_view),
    path('<str:sessionid>/status/', views.new_status),
    path('<str:sessionid>/<int:teamnumber>/', views.new_team_value),
]