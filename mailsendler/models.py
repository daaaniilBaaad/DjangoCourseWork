from django.db import models

from users.models import User


class MailGetter(models.Model): # Модель «Получатель рассылки»
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=255, verbose_name='Ф. И. О.')
    comment = models.TextField(blank=True, verbose_name='Комментарий')

    def __str__(self):
        return self.email


class MailMessage(models.Model): # Модель «Сообщение»
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец')
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Текст письма')

    def __str__(self):
        return self.subject

class MailMailing(models.Model): # Модель «Рассылка»
    STATUS_CREATED = 'created'
    STATUS_RUNNING = 'running'
    STATUS_FINISHED = 'finished'

    STATUS_CHOICES = [
        (STATUS_CREATED, 'Создана'),
        (STATUS_RUNNING, 'Запущена'),
        (STATUS_FINISHED, 'Завершена'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(verbose_name='Дата/Время начала')
    end_time = models.DateTimeField(verbose_name='Дата/Время окончания')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='created',
        verbose_name='Статус',
    )

    message = models.ForeignKey(MailMessage, on_delete=models.CASCADE)
    getters = models.ManyToManyField(MailGetter)

    def __str__(self):
        return f'Рассылка #{self.id} - {self.get_status_display()}'

class MailAttempt(models.Model): # Модель «Попытка рассылки»
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failed', 'Не успешно'),
    ]

    attempt_time = models.DateTimeField(auto_now_add=True) # Дата и время попытки
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    server_response = models.TextField(blank=True)
    mailing = models.ForeignKey(
        MailMailing,
        on_delete=models.CASCADE,
        related_name='attempts'
    )

    def __str__(self):
        return f'Попытка отправки рассылки #{self.mailing.id} - {self.get_status_display()}'
