from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="api_index"),
    path("register/", views.RegisterView.as_view(), name="api_register"),
    path("verify-registration/", views.VerifyRegistrationView.as_view(), name="api_verify_registration"),
    path("login/", views.LoginView.as_view(), name="api_login"),
    path("logout/", views.LogoutView.as_view(), name="api_logout"),
    path("forgot-password/request/", views.ForgotPasswordRequestView.as_view(), name="api_forgot_password_request"),
    path("forgot-password/verify/", views.ForgotPasswordVerifyView.as_view(), name="api_forgot_password_verify"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("notes/", views.FetchNotesView.as_view(), name="api_fetch_notes"),
    path("notes/create/", views.CreateNoteView.as_view(), name="api_create_note"),
    path("notes/edit/<int:note_id>/", views.EditNoteView.as_view(), name="api_edit_note"),
    path("notes/delete/<int:note_id>/", views.DeleteNoteView.as_view(), name="api_delete_note"),
]