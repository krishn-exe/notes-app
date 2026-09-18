from django.http import HttpResponse

def index(request):
    return HttpResponse("Welcome to the API index page.")

def register(request):
    return HttpResponse("This is the registration page.")

def login(request):
    return HttpResponse("This is the login page.")