from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the Notes App")

def register(request):
    return HttpResponse("Register Page")

def login(request):
    return HttpResponse("Login Page")

def logout(request):
    return HttpResponse("Logout Page")
