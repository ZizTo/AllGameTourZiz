from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, SearchForm
from .models import User, GameStats
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
                              {"user": request.user, "loginForm": loginForm, "error": "bad login or password, bro"})
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
    context = {"user": request.user}

    context['viewuser'] = user
    context['stats'] = user.gamestats_set.all()

    return render(request, "profile.html", context)


MAX_ON_PAGE = 5

def all_profiles_view(request):
    search = request.GET.get('search', '')
    if not bool(re.match(r"^[a-zA-Z0-9 ]+$", search)) or len(search) > 20:
        search = ''

    searchparam = f"/users/?search={search}" if search else "/users/"
    try:
        page = int(request.GET.get("page", 1))
        lastpage = math.floor(((User.objects.filter(username__icontains=search).count() - 1) / MAX_ON_PAGE) + 1)
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
    filtredusers = User.objects.filter(username__icontains=search)
    usersonpage = filtredusers.order_by("-MMR", "username")[(page-1)*MAX_ON_PAGE:page*MAX_ON_PAGE]
    context['allusers'] = usersonpage.values("username", "avatar", "MMR")

    return render(request, "allprofiles.html", context)