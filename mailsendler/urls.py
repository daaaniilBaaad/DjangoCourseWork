from django.urls import path
from . import views

app_name = "mailsendler"

urlpatterns = [
    # Главная
    path("", views.IndexView.as_view(), name="main_page"),

    # Попытки рассылок
    path("attempts/", views.MailingAttemptsView.as_view(), name="mailing_attempts"),

    # Рассылки CRUD
    path("mailings/", views.MailingListView.as_view(), name="mailing_list"),
    path("mailings/create/", views.MailingCreateView.as_view(), name="create_mailing"),
    path("mailings/<int:pk>/edit/", views.MailingUpdateView.as_view(), name="edit_mailing"),
    path("mailings/<int:pk>/", views.MailingDetailView.as_view(), name="mailing_detail"),
    path("mailings/<int:pk>/delete/", views.MailingDeleteView.as_view(), name="delete_mailing"),
    path("mailings/<int:mailing_id>/stop/", views.StopMailingView.as_view(), name="stop_mailing"),

    # Получатели CRUD
    path("getters/", views.GetterListView.as_view(), name="getter_list"),
    path("getters/create/", views.GetterCreateView.as_view(), name="create_getter"),
    path("getters/<int:pk>/edit/", views.GetterUpdateView.as_view(), name="edit_getter"),
    path("getters/<int:pk>/", views.GetterDetailView.as_view(), name="getter_detail"),
    path("getters/<int:pk>/delete/", views.GetterDeleteView.as_view(), name="delete_getter"),

    # Пользователи (только staff)
    path("users/", views.UsersListView.as_view(), name="users_list"),
    path("users/<int:user_id>/block/", views.BlockUserView.as_view(), name="block_user"),
]
