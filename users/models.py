from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    def validate_image(self):
        filesize = self.file.size
        megabyte_limit = 2
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError(f"Максимальный размер файла не должен превышать {megabyte_limit} МБ")

    username = None
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField(upload_to="images/avatar", null=True, blank=True, validators=[validate_image],
                               verbose_name=_('аватарка'))
    name = models.CharField(max_length=100, null=True, blank=False, verbose_name=_('имя пользователя'))
    phoneNumberRegex = RegexValidator(regex=r"^\d{10}$", message="Номер должен содержать 10 цифр")
    phone = models.CharField(validators=[phoneNumberRegex], max_length=10, unique=True,
                             verbose_name=_('телефон'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('пользователь')
        verbose_name_plural = _('пользователи')

    def __str__(self):
        return self.email
