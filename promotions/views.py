from django.views.generic import ListView, DetailView
from promotions.models import Promo
from product.services import get_category
from promotions.services import get_active_promotions, get_related_products
from django.conf import settings


class PromoListView(ListView):
    template_name = 'promotions/promo-list.html'
    context_object_name = 'promotions'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        return context

    def get_queryset(self):
        return get_active_promotions()

    def get_paginate_by(self, queryset):
        promo_per_page = self.request.session.get(settings.ADMIN_SETTINGS_ID)
        if promo_per_page is None or promo_per_page.get('PROMO_PER_PAGE') is None:
            paginator = settings.PROMO_PER_PAGE
        else:
            paginator = promo_per_page['PROMO_PER_PAGE']
        return paginator


class PromoDetailView(DetailView):
    template_name = 'promotions/promo-detail.html'
    model = Promo
    context_object_name = 'promo'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        products = get_related_products(self.object, self.request)
        context['page_obj'] = products
        return context
