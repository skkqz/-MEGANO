from django.contrib import messages
from django.contrib.auth import authenticate, login
# from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect

from product.models import HistoryView
from users.forms import CustomUserChangeForm
from users.models import CustomUser
from django.views.generic import DetailView, View, ListView
from product.services import get_category
from product.models import Offer
from .models import Seller
from orders.models import OrderItem, Order
from .service import SiteSettings
from .forms import SiteSettingsForm
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
import os


class SellerInfo(DetailView):
    model = Seller
    template_name = 'shop/seller.html'
    context_object_name = 'seller'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        popular = {}
        popular_queryset = OrderItem.objects.filter(offer__seller_id=self.object.id). \
            values_list('offer__id', 'quantity')
        for i in popular_queryset:
            if i[0] in popular:
                popular[str(i[0])] += int(i[1])
            else:
                popular[str(i[0])] = int(i[1])
        context['popular'] = Offer.objects.filter(pk__in=sorted(popular, reverse=True)[:10])
        context['categories'] = get_category()
        return context


class SiteSettingsView(PermissionRequiredMixin, View):

    permission_required = ('orders.add_order', )

    def get(self, request):
        site = SiteSettings(request)
        form = SiteSettingsForm()
        name = ['PROMO_PER_PAGE', 'PROMO_PRODUCTS_PER_PAGE', 'CATALOG_PRODUCT_PER_PAGE',
                'CACHE_STORAGE_TIME', 'DELIVERY_PRICE']
        return render(request, 'shop/site_settings.html', {'site': site, 'form': form, 'name': name})

    def post(self, request):
        site_settings = SiteSettings(request)
        form = SiteSettingsForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            site_settings.add(name=cd['name'],
                              value=cd['value'])
            site_settings.save()
            return redirect('settings')


class AccauntView(ListView):
    template_name = 'shop/accaunt.html'
    model = HistoryView

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        histories = HistoryView.objects.filter(user=self.request.user)[:3]
        orders = Order.objects.filter(email=self.request.user).first()
        context['histories'] = histories
        context['orders'] = orders
        context['categories'] = get_category()
        return context


class AccauntEditView(View):
    def get(self, request):
        accaunt_form = CustomUserChangeForm(instance=request.user)
        # password_change_form = PasswordChangeForm(user=request.user)
        return render(request, 'shop/accaunt_edit.html', context={
            'accaunt_form': accaunt_form, 'categories': get_category()})

    def post(self, request):
        accaunt_form = CustomUserChangeForm(request.POST, files=request.FILES, instance=request.user)
        # password_change_form = PasswordChangeForm(user=request.user, data=request.POST)
        if accaunt_form.is_valid():
            pas_first = request.POST.get("password")
            pas_second = request.POST.get("passwordReply")
            accaunt_form.save()
            user_accaunt = CustomUser.objects.get(email=request.user)
            if pas_first == pas_second and pas_first != '':
                user_accaunt.set_password(pas_first)
                user_accaunt.save()
                user = authenticate(email=request.user, password=pas_first)
                login(request, user)
            messages.success(request, 'Профиль успешно изменён')
            return HttpResponseRedirect('accaunt_edit')
        else:
            return render(request, 'shop/accaunt_edit.html',
                          {'accaunt_form': accaunt_form,  'categories': get_category()})


class UrlsView(View):

    def get(self, request):
        path = os.path.join(os.path.dirname(__file__), 'urls.txt')
        with open(path, 'r') as file:
            data = file.readlines()
            return render(request, 'shop/urls.html', {'data': data})
