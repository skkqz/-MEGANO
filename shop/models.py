from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser


class Seller(models.Model):
    """Продавец"""
    user = models.OneToOneField(CustomUser, verbose_name=_('пользователь'), on_delete=models.CASCADE)
    name = models.CharField(max_length=128, verbose_name=_('имя продавца'))
    description = models.CharField(max_length=1024, verbose_name=_('описание'))
    address = models.CharField(max_length=128, verbose_name=_('адрес'))
    number = models.IntegerField(validators=[MinValueValidator(100000), MaxValueValidator(89999999999)],
                                 verbose_name=_('номер телефона'))

    class Meta:
        verbose_name = _('продавец')
        verbose_name_plural = _('продавцы')

    def __str__(self):
        return self.name


class SellerLogo(models.Model):
    """Логотип продавца"""
    seller = models.OneToOneField(Seller, verbose_name=_('продавец'),
                                  on_delete=models.CASCADE, related_name='logo')
    image = models.ImageField(upload_to='static/img/', verbose_name=_("логотип продавца"))

    class Meta:
        verbose_name = _('логотип продавца')
        verbose_name_plural = _('логотипы продавцов')

    def __str__(self):
        return self.seller.name
