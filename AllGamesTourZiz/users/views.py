from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm

def loginView(request):
    if request.method == 'POST':
        loginForm = LoginForm(request.POST)
        if loginForm.is_valid():
            username = loginForm.cleaned_data['login']
            password = loginForm.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return HttpResponseRedirect("/users/login/")
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

# Create your views here.
