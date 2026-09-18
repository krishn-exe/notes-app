from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="api_index"),
    path("register/", views.register, name="api_register"),
    path("login/", views.login, name="api_login"),
]
