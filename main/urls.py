from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("create/", views.create_note, name="create_note"),
    path("edit/<int:note_id>/", views.edit_note, name="edit_note"),
    path("delete/<int:note_id>/", views.delete_note, name="delete_note"),
]
