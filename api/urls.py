from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="api_index"),
    path("register/", views.register, name="api_register"),
    path("login/", views.login, name="api_login"),
    path("logout/", views.logout, name="api_logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
