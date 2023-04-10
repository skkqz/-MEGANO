from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Min

from users.models import CustomUser


class Product(models.Model):
    """Продукт"""
    name = models.CharField(max_length=128, verbose_name=_("наименование"))
    description = models.CharField(max_length=1024, verbose_name=_("описание"))
    seller = models.ManyToManyField("shop.Seller", through="Offer", verbose_name=_("продавец"))
    property = models.ManyToManyField("Property", through="ProductProperty", verbose_name=_("характеристики"))
    category = models.ForeignKey("Category", on_delete=models.CASCADE, blank=True, null=True,
                                 related_name="products", verbose_name=_("категория"))
    is_limited = models.BooleanField(default=False, verbose_name=_('ограниченный тираж'))

    class Meta:
        verbose_name = _("продукт")
        verbose_name_plural = _("продукты")
        ordering = ['id']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """ Возвращает урл на продукт """
        return reverse('product-detail', args=[str(self.id)])


class Property(models.Model):
    """Свойство продукта"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("свойство")
        verbose_name_plural = _("свойства")


class ProductProperty(models.Model):
    """Значение свойства продукта"""
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("продукт"))
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='prod', verbose_name=_("свойство"))
    value = models.CharField(max_length=128, verbose_name=_("значение"))

    class Meta:
        verbose_name = _("свойство продукта")
        verbose_name_plural = _("свойства продуктов")


class Banner(models.Model):
    """ Баннеры. """
    title = models.CharField(max_length=128, verbose_name=_('заголовок'))
    brief = models.CharField(max_length=512, verbose_name=_('краткое описание'))
    icon = models.ImageField(upload_to='images/banners/', verbose_name=_('изображение'))
    added_at = models.DateTimeField(auto_created=True, auto_now=True, verbose_name=_("дата добавления"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='banners', verbose_name=_("продукт"))
    is_active = models.BooleanField(default=False, verbose_name=_("активность"))

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """ Возвращает урл на продукт """
        return self.product.get_absolute_url()

    class Meta:
        verbose_name = _("баннер")
        verbose_name_plural = _("баннеры")


class Category(MPTTModel):
    """Категория продукта"""
    STATUS_CHOICE = [
        (True, _("Активна")),
        (False, _("Не активна")),
    ]

    name = models.CharField(max_length=100, verbose_name=_("категория"))
    icon = models.FileField(upload_to="images/icons/", verbose_name=_("иконка"), blank=True)
    active = models.BooleanField(choices=STATUS_CHOICE, default=False, verbose_name=_("активность"))
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                            related_name="children", verbose_name=_("родитель"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("категория")
        verbose_name_plural = _("категории")

    def save(self, *args, **kwargs):
        if not self.parent:
            pass
        elif self.parent.level >= 2:
            raise ValueError('Достигнута максимальная вложенность!')
        super(Category, self).save(*args, **kwargs)

    def min_price(self):
        """Возвращает минимальную стоимость товара в категории."""
        result = Product.objects.select_related('category'). \
            filter(category_id=self.pk).aggregate(min_price=Min('offers__price'))
        return result['min_price']


class Offer(models.Model):
    """Товар"""
    product = models.ForeignKey("Product", on_delete=models.PROTECT, related_name='offers', verbose_name=_("продукт"))
    seller = models.ForeignKey("shop.Seller", on_delete=models.PROTECT,
                               related_name='sellers', verbose_name=_("продавец"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('цена'))
    added_at = models.DateTimeField(auto_created=True, auto_now=True, verbose_name=_('время добавления'))
    is_free_delivery = models.BooleanField(default=True, verbose_name=_('бесплатная доставка'))
    is_present = models.BooleanField(default=True, verbose_name=_('в наличии'))

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = _("товар")
        verbose_name_plural = _("товары")


class ProductImage(models.Model):
    """Фотографии продукта"""
    product = models.ForeignKey(Product, verbose_name=_('продукт'), on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/', verbose_name=_("изображение продукта"))

    class Meta:
        verbose_name = _('изображение продукта')
        verbose_name_plural = _('изображения продуктов')

    def __str__(self):
        return self.product.name


class HistoryView(models.Model):
    """История просмотра товаров"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='views_user')
    view_at = models.DateTimeField(auto_now=True, verbose_name=_('время просмотра'))
    offer = models.ForeignKey(Offer, verbose_name=_('товар'), on_delete=models.CASCADE, related_name='views')

    class Meta:
        ordering = ('-view_at',)
        verbose_name = _("история просмотров")
        verbose_name_plural = _("истории просмотров")

    def __str__(self):
        return self.offer.product.name


class Feedback(models.Model):
    """Отзыв"""

    grate_list = [
        (1, '1 🌟'),
        (2, '2 🌟'),
        (3, '3 🌟'),
        (4, '4 🌟'),
        (5, '5 🌟'),
    ]

    offer = models.ForeignKey(Offer, verbose_name=_('товар'), on_delete=models.PROTECT, blank=True, null=True)
    author = models.ForeignKey(get_user_model(), verbose_name=_('автор'), on_delete=models.PROTECT)
    publication_date = models.DateTimeField(auto_now=True, verbose_name=_("дата публикации"))
    rating = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)], choices=grate_list,
                                 verbose_name=_('рейтинг'))
    description = models.TextField(max_length=2048, verbose_name=_('описание'))
    image = models.ImageField(upload_to='feedback_images/', blank=True, verbose_name=_('фотография'))

    class Meta:
        verbose_name = _('отзыв')
        verbose_name_plural = _('отзывы')

    def __str__(self):
        return self.offer.product.name


class LoggingImportFileModel(models.Model):
    """Модель логирование ошибок импорта файла"""

    file_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Имя файла'))
    seller = models.ForeignKey("shop.Seller", on_delete=models.PROTECT, related_name='seller_log')
    message = models.CharField(max_length=255, verbose_name=_('Текст ошибки'))
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Логирование')
        verbose_name_plural = _('Логирование')

    def __str__(self):
        return self.file_name
