from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from product.models import Offer

# STATUS_CHOICES = (
#     ('W', _('ожидание ответа от продавца')),
#     ('A', _('продавец принял заказ')),
#     ('M', _('упаковка на складе')),
#     ('S', _('в пути')),
#     ('F', _('прибыл в пункт выдачи')),
# )
DELIVERY_CHOICES = (
    ('D', _('доставка')),
    ('A', _('экспресс доставка')),
)
TYPE_CHOICES = (
    ('C', _('онлайн картой')),
    ('F', _('онлайн со случайного чужого счета')),
)


class Order(models.Model):
    first_name = models.CharField(max_length=50, verbose_name=_("имя"))
    last_name = models.CharField(max_length=50, verbose_name=_("фамилия"))
    email = models.EmailField(verbose_name=_("почта"))
    offer = models.ManyToManyField(Offer, through="OrderItem", verbose_name=_("товар"))
    address = models.CharField(max_length=250, blank=True, null=True, verbose_name=_("адрес"))
    number = models.IntegerField(validators=[MinValueValidator(100000), MaxValueValidator(89999999999)],
                                 verbose_name=_('номер телефона'))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("город"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("дата создания"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("дата обновления"))
    paid = models.BooleanField(default=False, verbose_name=_("статус оплаты"))
    delivery = models.CharField(max_length=1, choices=DELIVERY_CHOICES, default='D', verbose_name=_('тип доставки'))
    status = models.CharField(max_length=50, verbose_name=_('статус заказа'), null=True, blank=True)
    payment = models.CharField(max_length=1, choices=TYPE_CHOICES, default='C', verbose_name=_('тип оплаты'),
                               null=True, blank=True)
    card_number = models.PositiveIntegerField(validators=[MinValueValidator(10000000), MaxValueValidator(99999999)],
                                              verbose_name=_('номер карты'), null=True)
    status_payment = models.CharField(max_length=50, verbose_name=_('статус платежа'), null=True, blank=True)
    payment_code = models.IntegerField(default=0, verbose_name=_('код оплаты'))
    total = models.IntegerField(default=0, verbose_name=_('общая стоимость'))
    comment = models.CharField(max_length=500, blank=True, null=True, verbose_name=_("адрес"))

    class Meta:
        ordering = ('-created',)
        verbose_name = _('заказ')
        verbose_name_plural = _('заказы')

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.PROTECT, verbose_name=_("заказ"))
    offer = models.ForeignKey(Offer, related_name='order_items', on_delete=models.PROTECT, verbose_name=_("товар"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("цена"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("количество"))

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = _('товар в заказе')
        verbose_name_plural = _('товары в заказах')
