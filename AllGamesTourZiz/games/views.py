from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import Game
import re
import math

MAX_ON_PAGE = 5


def all_games_view(request):
    search = request.GET.get('search', '')
    if not bool(re.match(r"^[a-zA-Z0-9 ]+$", search)) or len(search) > 20:
        search = ''

    new_link = f"/games/?search={search}" if search else "/games/"

    filtered_games = Game.objects.filter(name__icontains=search).filter(relateOnId=None)
    try:
        page = int(request.GET.get("page", 1))
        last_page = max(math.floor(((filtered_games.count() - 1) / MAX_ON_PAGE) + 1), 1)
        if page < 1 or page > last_page:
            raise
    except:
        return HttpResponseRedirect(new_link)

    context = {"user": request.user, 'page': page}
    if page > 1:
        context['prevpage'] = new_link + (f'&page={page-1}' if search else f"?page={page-1}")
    if page < last_page:
        context['nextpage'] = new_link + (f'&page={page+1}' if search else f"?page={page+1}")
    if search != '':
        context['search'] = search

    context['allgames'] = filtered_games[(page-1)*MAX_ON_PAGE:page*MAX_ON_PAGE].values("name", "image")

    return render(request, "allgames.html", context)


def game_view(request, gamename):
    games = Game.objects.filter(name=gamename)
    if not games.exists():
        return render(request, "errors/game_not_found.html", {"user": request.user})

    game = games.first()
    users = game.gamestats_set.order_by("-MMR")[0:MAX_ON_PAGE]
    context = {"user": request.user, 'game': game,
               'users': users.values("user__username", "user__avatar", "MMR"),
               'undergames': game.game_set.all().values("name", "image", "description")}

    if game.relateOnId is not None:
        context['upgamename'] = game.relateOnId.name
        context['upgameimage'] = game.relateOnId.image

    return render(request, "game.html", context)
