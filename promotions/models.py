from django.db import models
from django.utils.translation import gettext_lazy as _
from product.models import Product


class PromoType(models.Model):
    """Описывает тип акции или модели скидки."""
    name = models.CharField(max_length=128, verbose_name=_('название типа скидки'))
    code = models.PositiveSmallIntegerField(
        verbose_name=_('код'),
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("тип скидки")
        verbose_name_plural = _("типы скидок")


class Promo(models.Model):
    """Описывает модель акций/скидок."""
    name = models.CharField(max_length=128, verbose_name=_('название акции'))
    promo_type = models.ForeignKey(PromoType, related_name='promos',
                                   on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/promotions/",
                              verbose_name=_("изображение"), blank=True)
    description = models.TextField(verbose_name=_('описание'))
    fix_discount = models.DecimalField(verbose_name=_('фиксированная сумма скидки'),
                                       decimal_places=2, max_digits=6,
                                       default=0.00)
    discount = models.PositiveSmallIntegerField(
        verbose_name=_('размер скидки в процентах'),
        default=0
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name=_('количество единиц товара в акции'),
        default=1
    )
    amount = models.DecimalField(
        verbose_name=_('сумма, с которой начинает действовать скидка'),
        decimal_places=2, max_digits=8, default=0.00)
    started = models.DateField(verbose_name=_('начало действия скидки'), blank=True, null=True)
    finished = models.DateField(verbose_name=_('окончание действия скидки'))
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("акция")
        verbose_name_plural = _("акции")
        ordering = ['id']


class Promo2Product(models.Model):
    """Связывает модели акций и продуктов."""
    promo = models.ForeignKey(Promo, related_name='promo2products',
                              on_delete=models.CASCADE,
                              verbose_name=_('акция'))
    product = models.ManyToManyField(Product, related_name='promo2products',
                                     verbose_name=_('товар в акции'))

    def __str__(self):
        return f"Товары в {self.promo.name!r}"

    class Meta:
        verbose_name = _("товары в акции")
        verbose_name_plural = _("товары в акциях")
