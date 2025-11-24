from django.urls import path

from . import views
from .views import (
    RegisterView,
    UserLoginView,
    UserLogoutView,
    email_verification,
    UserPasswordResetView,
    UserPasswordResetDoneView,
    UserPasswordResetConfirmView,
    UserPasswordResetCompleteView, UserProfileView, UserProfileUpdateView,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("email-confirm/<str:token>/", email_verification, name="email_confirm"),
    path("block/<int:user_id>/", views.toggle_user_block, name="toggle_block"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("profile/edit/", UserProfileUpdateView.as_view(), name="profile_edit"),

    # Сброс пароля
    path("password-reset/", UserPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", UserPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password-reset/confirm/<uidb64>/<token>/", UserPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password-reset/complete/", UserPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
