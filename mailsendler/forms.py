from django import forms
from django.forms import BooleanField
from .models import MailMailing, MailGetter


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fild_name, fild in self.fields.items():
            if isinstance(fild, BooleanField):
                fild.widget.attrs['class'] = 'form-check-input'
            else:
                fild.widget.attrs['class'] = 'form-control'


# Форма для рассылок
class MailMailingForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = MailMailing
        fields = ['start_time', 'end_time', 'status', 'message', 'getters']  # указать реальные поля модели


# Форма для клиентов
class MailGetterForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = MailGetter
        fields = ['email', 'full_name', 'comment']  # указать реальные поля модели


BANNED_WORDS = [
    'казино', 'криптовалюта', 'крипта', 'биржа',
    'дешево', 'бесплатно', 'обман', 'полиция', 'радар'
]