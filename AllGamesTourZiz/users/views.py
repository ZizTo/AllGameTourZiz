from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, SearchForm
from .models import User, GameStats
from playSessions.models import SessionParticipants, PlaySession
import math
import re


def loginView(request):
    if request.method == 'POST':
        loginForm = LoginForm(request.POST)
        if loginForm.is_valid():
            username = loginForm.cleaned_data['login']
            password = loginForm.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return HttpResponseRedirect(f"/users/{username}")
            else:
                return render(request, "loginpage.html",
                              {"user": request.user, "loginForm": loginForm,
                               "error": "bad login or password, bro"})
        else:
            return HttpResponse("<h1>Data is not valid</h1>")
    elif request.method == 'GET':
        loginForm = LoginForm()
        return render(request, "loginpage.html", {"user": request.user, "loginForm": loginForm})
    else:
        return HttpResponse("<h1>No method found</h1>")


def logoutView(request):
    logout(request)
    return HttpResponseRedirect("/users/login/")


def profile_view(request, usname):
    users = User.objects.filter(username=usname)
    if not users.exists():
        return render(request, "errors/user_not_found.html", {"user": request.user})

    user = users.first()
    context = {"user": request.user,
               'viewuser': user,
               'stats': user.gamestats_set.all()}

    # --------
    filtered_sessions_participants = SessionParticipants.objects.filter(user=user).order_by("-session__created_at")
    context['allsessions'] = filtered_sessions_participants.values("session__uniqueCode",
                                                    "session__status", "session__game__name", "session__game__image")

    for i in range(len(context['allsessions'])):
        this_session_participants = SessionParticipants.objects.filter(session=filtered_sessions_participants[i].session)

        player1 = this_session_participants.filter(numberInSession=0).first()
        if player1 is None:
            continue

        context['allsessions'][i]['player1name'] = player1.user.username
        context['allsessions'][i]['player1avatar'] = player1.user.avatar
        player2 = this_session_participants.filter(numberInSession=1).first()

        if player2 is None:
            continue

        context['allsessions'][i]['player2name'] = player2.user.username
        context['allsessions'][i]['player2avatar'] = player2.user.avatar

        context['allsessions'][i]['player3exists'] = this_session_participants.filter(numberInSession=2).exists()

    return render(request, "profile.html", context)


MAX_ON_PAGE = 5


def all_profiles_view(request):
    search = request.GET.get('search', '')
    if not bool(re.match(r"^[a-zA-Z0-9 ]+$", search)) or len(search) > 20:
        search = ''

    new_link = f"/users/?search={search}" if search else "/users/"

    filtered_users = User.objects.filter(username__icontains=search)
    try:
        page = int(request.GET.get("page", 1))
        lastpage = max(math.floor(((filtered_users.count() - 1) / MAX_ON_PAGE) + 1), 1)
        if page < 1 or page > lastpage:
            return HttpResponseRedirect(new_link)
    except:
        return HttpResponseRedirect(new_link)

    context = {"user": request.user, 'page': page}
    if page > 1:
        context['prevpage'] = new_link + (f'&page={page-1}' if search else f"?page={page-1}")
    if page < lastpage:
        context['nextpage'] = new_link + (f'&page={page+1}' if search else f"?page={page+1}")
    if search != '':
        context['search'] = search

    users_on_page = filtered_users.order_by("-MMR", "username")[(page-1)*MAX_ON_PAGE:page*MAX_ON_PAGE]
    context['allusers'] = users_on_page.values("username", "avatar", "MMR")

    return render(request, "allprofiles.html", context)