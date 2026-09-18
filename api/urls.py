from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="api_index"),
    path("register/", views.register, name="api_register"),
    path("login/", views.login, name="api_login"),
    path("logout/", views.logout, name="api_logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("notes/", views.FetchNotes, name="api_fetch_notes"),
    path("notes/create/", views.CreateNote, name="api_create_note"),
    path("notes/edit/<int:note_id>/", views.EditNote, name="api_edit_note"),
    path("notes/delete/<int:note_id>/", views.DeleteNote, name="api_delete_note"),
]