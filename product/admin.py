from django.contrib import admin  # noqa F401
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin
from shop.models import Seller
from product.models import (
    Product,
    Banner,
    Category,
    Offer,
    ProductProperty,
    Feedback,
    HistoryView,
    ProductImage,
    Property,
)


class ProductInLine(admin.TabularInline):
    model = Product.property.through


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_limited']
    inlines = [ProductInLine, ]
    list_editable = ['is_limited']

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(ProductAdmin, self).get_queryset(request)
        else:
            qs = super(ProductAdmin, self).get_queryset(request)
            return qs.filter(seller__user=request.user)

    class Meta:
        verbose_name = _('товар')
        verbose_name_plural = _('товары')


class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'added_at', 'is_active']
    list_editable = ['is_active']

    class Meta:
        verbose_name = _('баннер')
        verbose_name_plural = _('баннеры')


class CategoryAdmin(MPTTModelAdmin):
    list_display = ['name', 'active', 'parent', 'icon']

    class Meta:
        verbose_name = _('категория')
        verbose_name_plural = _('категории')


class OfferAdmin(admin.ModelAdmin):
    list_display = ['product', 'seller', 'price', 'is_free_delivery', 'is_present']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        if not is_superuser:
            disabled_fields |= {
                'seller',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(OfferAdmin, self).get_queryset(request)
        else:
            qs = super(OfferAdmin, self).get_queryset(request)
            return qs.filter(seller__user=request.user)

    def get_exclude(self, request, obj=None):
        excluded = super().get_exclude(request, obj) or []

        if not obj and not request.user.is_superuser:
            return excluded + ['seller']
        return excluded

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.seller = Seller.objects.get(user=request.user)
        return super().save_model(request, obj, form, change)

    class Meta:
        verbose_name = _('цена')
        verbose_name_plural = _('цены')


class PropertyAdmin(admin.ModelAdmin):
    list_display = ['name', ]

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(PropertyAdmin, self).get_queryset(request)
        else:
            qs = super(PropertyAdmin, self).get_queryset(request)
            return qs.filter(product__seller__user=request.user)


class ProductPropertyAdmin(admin.ModelAdmin):
    list_display = ['product', 'property', 'value']

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(ProductPropertyAdmin, self).get_queryset(request)
        else:
            qs = super(ProductPropertyAdmin, self).get_queryset(request)
            return qs.filter(product__seller__user=request.user)


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super(ProductImageAdmin, self).get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            product = Product.objects.filter(seller__user=request.user)
            form.base_fields['product'].queryset = product
        return form

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(ProductImageAdmin, self).get_queryset(request)
        else:
            qs = super(ProductImageAdmin, self).get_queryset(request)
            return qs.filter(product__seller__user=request.user)

    class Meta:
        verbose_name = _('изображение продукта')
        verbose_name_plural = _('изображения продуктов')


class HistoryViewAdmin(admin.ModelAdmin):
    """ТЕСТ истории просмотра"""
    list_display = ['offer', 'view_at']

    class Meta:
        verbose_name = _('история просмотров')
        verbose_name_plural = _('истории просмотров')


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['offer', 'author', 'publication_date', 'rating', 'description', 'image']


admin.site.register(Product, ProductAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(ProductProperty, ProductPropertyAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(HistoryView, HistoryViewAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Feedback, FeedbackAdmin)
