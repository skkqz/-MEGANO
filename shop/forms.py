from django import forms

names = (('PROMO_PER_PAGE', 'PROMO_PER_PAGE'), ('PROMO_PRODUCTS_PER_PAGE', 'PROMO_PRODUCTS_PER_PAGE'),
         ('CATALOG_PRODUCT_PER_PAGE', 'CATALOG_PRODUCT_PER_PAGE'), ('CACHE_STORAGE_TIME', 'CACHE_STORAGE_TIME'),
         ('DELIVERY_PRICE', 'DELIVERY_PRICE'))


class SiteSettingsForm(forms.Form):
    name = forms.ChoiceField(choices=names)
    value = forms.IntegerField(label='Значение')
