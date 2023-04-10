from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'phone')


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'phone', 'avatar')
        error_messages = {
            "name": {
                "required": "Поле ФИО является обязательным для заполнения",
            },
            "email": {
                "required": "Поле E-mail является обязательным для заполнения",
                'invalid': 'Не верно указан email'
            },
        }
