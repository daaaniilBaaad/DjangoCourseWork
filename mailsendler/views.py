from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
)

from mailsendler.models import (
    MailMailing as Mailing,
    MailGetter as Getter,
    MailAttempt as MailingAttempt, MailGetter, MailMessage, MailMailing,
)
from users.models import User
from mailsendler.forms import MailMailingForm, MailGetterForm, MailMessageForm
from django.utils import timezone


# --------------------------
# РОЛЬ МЕНЕДЖЕРА
# --------------------------
def is_manager(user):
    return user.groups.filter(name="Менеджер").exists()


# --------------------------
# Home Page
# --------------------------
class IndexView(TemplateView):
    template_name = 'mailsendler/main_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing_total'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status=Mailing.STATUS_RUNNING).count()
        context['unique_clients'] = Getter.objects.values('email').distinct().count()
        return context


# --------------------------
# Mailing List
# --------------------------
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailsendler/mailing_list.html'

    def get_queryset(self):
        user = self.request.user
        if is_manager(user):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)


# --------------------------
# Mailing Detail
# --------------------------
class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailsendler/mailing_detail.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        # Пользователь видит только своё, менеджер всё
        if obj.owner != request.user and not is_manager(request.user):
            return redirect('mailsendler:mailing_list')
        return super().dispatch(request, *args, **kwargs)


# --------------------------
# Create Mailing
# --------------------------
class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailMailingForm
    template_name = 'mailsendler/mailing_form.html'
    success_url = reverse_lazy('mailsendler:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


# --------------------------
# Update Mailing (только владелец)
# --------------------------
class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailMailingForm
    template_name = 'mailsendler/mailing_form.html'
    success_url = reverse_lazy('mailsendler:mailing_list')

    def dispatch(self, request, *args, **kwargs):
        mailing = self.get_object()
        if mailing.owner != request.user:  # менеджер не может редактировать
            return redirect('mailsendler:mailing_list')
        return super().dispatch(request, *args, **kwargs)


# --------------------------
# Delete Mailing
# --------------------------
class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailsendler/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailsendler:mailing_list')

    def dispatch(self, request, *args, **kwargs):
        mailing = self.get_object()
        if mailing.owner != request.user:  # менеджер не может удалять
            return redirect('mailsendler:mailing_list')
        return super().dispatch(request, *args, **kwargs)


# --------------------------
# Stop Mailing (только менеджер)
# --------------------------
class StopMailingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not is_manager(request.user):
            return redirect('mailsendler:mailing_list')

        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.status = Mailing.COMPLETED
        mailing.save()

        messages.success(request, "Рассылка завершена менеджером.")
        return redirect('mailsendler:mailing_detail', pk=pk)


# --------------------------
# Getter List
# --------------------------
class GetterListView(LoginRequiredMixin, ListView):
    model = MailGetter
    template_name = 'mailsendler/getter_list.html'

    def get_queryset(self):
        user = self.request.user
        if is_manager(user):
            return MailGetter.objects.all()
        return MailGetter.objects.filter(owner=user)


# --------------------------
# Getter Create
# --------------------------
class GetterCreateView(LoginRequiredMixin, CreateView):
    model = Getter
    form_class = MailGetterForm
    template_name = 'mailsendler/getter_form.html'
    success_url = reverse_lazy('mailsendler:getter_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


# --------------------------
# Getter Update (только владелец)
# --------------------------
class GetterUpdateView(LoginRequiredMixin, UpdateView):
    model = Getter
    form_class = MailGetterForm
    template_name = 'mailsendler/getter_form.html'
    success_url = reverse_lazy('mailsendler:getter_list')

    def dispatch(self, request, *args, **kwargs):
        getter = self.get_object()
        if getter.owner != request.user:  # менеджер не редактирует
            return redirect('mailsendler:getter_list')
        return super().dispatch(request, *args, **kwargs)


# --------------------------
# Getter Delete
# --------------------------
class GetterDeleteView(LoginRequiredMixin, DeleteView):
    model = Getter
    template_name = 'mailsendler/getter_confirm_delete.html'
    success_url = reverse_lazy('mailsendler:getter_list')

    def dispatch(self, request, *args, **kwargs):
        getter = self.get_object()
        if getter.owner != request.user:  # менеджер тоже не может
            return redirect('mailsendler:getter_list')
        return super().dispatch(request, *args, **kwargs)


class GetterDetailView(LoginRequiredMixin, DetailView):
    model = Getter
    template_name = 'mailsendler/getter_detail.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user and not is_manager(request.user):
            return redirect('mailsendler:getter_list')
        return super().dispatch(request, *args, **kwargs)


# --------------------------
# Mailing Attempts (Логи)
# --------------------------
class MailingAttemptsView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = 'mailsendler/mailing_attempts.html'

    def get_queryset(self):
        user = self.request.user
        qs = MailingAttempt.objects.all()
        if not is_manager(user):
            qs = qs.filter(mailing__owner=user)
        return qs.order_by('-attempt_time')


# --------------------------
# Users List (только менеджер)
# --------------------------
class UsersListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/users_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not is_manager(request.user):
            return redirect('mailsendler:mailing_list')
        return super().dispatch(request, *args, **kwargs)


# --------------------------
# Block User
# --------------------------
class BlockUserView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not is_manager(request.user):
            return redirect('users:users_list')

        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()

        return redirect('users:users_list')


class MessageListView(LoginRequiredMixin, ListView):
    model = MailMessage
    template_name = 'mailsendler/message_list.html'

    def get_queryset(self):
        return MailMessage.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = MailMessage
    form_class = MailMessageForm
    template_name = 'mailsendler/message_form.html'
    success_url = reverse_lazy('mailsendler:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = MailMessage
    form_class = MailMessageForm
    template_name = 'mailsendler/message_form.html'
    success_url = reverse_lazy('mailsendler:message_list')


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = MailMessage
    template_name = 'mailsendler/message_confirm_delete.html'
    success_url = reverse_lazy('mailsendler:message_list')


class MainPageView(TemplateView):
    template_name = 'mailsendler/main_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailing_count'] = MailMailing.objects.count()
        context['active_mailings'] = MailMailing.objects.filter(status='running').count()
        context['unique_clients'] = MailGetter.objects.count()
        context['messages_count'] = MailMessage.objects.count()