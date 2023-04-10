from django.contrib import admin
from promotions.models import PromoType, Promo, Promo2Product


class PromoInline(admin.TabularInline):
    model = Promo2Product
    filter_horizontal = ['product']
    extra = 0


class ProductInline(admin.TabularInline):
    model = Promo2Product.product.through
    extra = 0


@admin.register(PromoType)
class PromoTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    ordering = ['code']


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'started', 'finished', 'is_active']
    list_editable = ['is_active']
    inlines = [PromoInline]
