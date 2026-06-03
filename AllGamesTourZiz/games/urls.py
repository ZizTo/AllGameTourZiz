from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.all_games_view),
    path('<str:gamename>', views.game_view)
]