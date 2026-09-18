from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("draw.png", views.favicon, name="favicon"),
    path("create/", views.create_note, name="create_note"),
    path("edit/<int:note_id>/", views.edit_note, name="edit_note"),
    path("delete/<int:note_id>/", views.delete_note, name="delete_note"),
    path("delete-image/<int:image_id>/", views.delete_image, name="delete_image"),
    path("image/<int:image_id>/", views.serve_image, name="serve_image"),
]
