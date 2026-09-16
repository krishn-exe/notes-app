from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from . forms import RegisterForm, LoginForm

def index(request):
    return render(request, "index.html")

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {'form': form})

def login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("index")
    else:
        form = LoginForm()
    return render(request, "login.html", {'form': form})

def logout(request):
    auth_logout(request)
    return render(request, "logout.html")
