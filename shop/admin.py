from django.contrib import admin  # noqa F401
from django.utils.translation import gettext_lazy as _
from shop.models import Seller, SellerLogo


class SellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'description', 'address', 'number']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        if not is_superuser:
            disabled_fields |= {
                'user',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(SellerAdmin, self).get_queryset(request)
        else:
            qs = super(SellerAdmin, self).get_queryset(request)
            return qs.filter(user=request.user)

    class Meta:
        verbose_name = _('продавец')
        verbose_name_plural = _('продавцы')


class SellerLogoAdmin(admin.ModelAdmin):
    list_display = ['seller', 'image']

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
        verbose_name = _('логотип продавца')
        verbose_name_plural = _('логотипы продавцов')


admin.site.register(Seller, SellerAdmin)
admin.site.register(SellerLogo, SellerLogoAdmin)
