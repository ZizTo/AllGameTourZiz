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

    searchparam = f"/games/?search={search}" if search else "/games/"
    try:
        page = int(request.GET.get("page", 1))
        lastpage = math.floor(((Game.objects.filter(name__icontains=search).filter(relateOnId=None).count() - 1) / MAX_ON_PAGE) + 1)
        if page < 1 or page > lastpage:
            return HttpResponseRedirect(searchparam)
    except:
        return HttpResponseRedirect(searchparam)

    context = {"user": request.user, 'page': page}
    if page > 1:
        context['prevpage'] = searchparam + (f'&page={page-1}' if search else f"?page={page-1}")
    if page < lastpage:
        context['nextpage'] = searchparam + (f'&page={page+1}' if search else f"?page={page+1}")
    if search != '':
        context['search'] = search

    filtredgames = Game.objects.filter(name__icontains=search).filter(relateOnId=None)[(page-1)*MAX_ON_PAGE:page*MAX_ON_PAGE]
    context['allgames'] = filtredgames.values("name", "image")

    return render(request, "allgames.html", context)


def game_view(request, gamename):
    games = Game.objects.filter(name=gamename)
    if not games.exists():
        return render(request, "errors/game_not_found.html", {"user": request.user})

    game = games.first()
    context = {"user": request.user}

    context['game'] = game
    users = game.gamestats_set.order_by("-MMR")[0:MAX_ON_PAGE]
    context['users'] = users.values("user__username", "user__avatar", "MMR")
    context['undergames'] = game.game_set.all().values("name", "image", "description")
    if game.relateOnId is not None:
        context['upgamename'] = game.relateOnId.name
        context['upgameimage'] = game.relateOnId.image

    return render(request, "game.html", context)
