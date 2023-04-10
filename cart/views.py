from django.shortcuts import redirect, get_object_or_404, render
from django.views import View
from product.models import Offer
from .service import Cart
from .forms import CartAddProductForm
from django.conf import settings
from product.services import get_category


class CartAdd(View):

    def post(self, request, id):
        cart = Cart(request)
        offer = get_object_or_404(Offer, id=id)
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(offer=offer,
                     quantity=cd['quantity'],
                     update_quantity=cd['update'])
        return redirect('cart:cart')


class CartRemove(View):

    def post(self, request, id):
        cart = Cart(request)
        offer = get_object_or_404(Offer, id=id)
        cart.remove(offer)
        return redirect('cart:cart')


class CartDelete(View):

    def post(self, request):
        if request.session.get(settings.CART_SESSION_ID):
            del request.session[settings.CART_SESSION_ID]
        return redirect('/')


class AddQuantity(View):
    def post(self, request, id):
        cart = Cart(request)
        offer = get_object_or_404(Offer, id=id)
        cart.add_quantity(offer)
        return redirect('cart:cart')


class RemoveQuantity(View):
    def post(self, request, id):
        cart = Cart(request)
        offer = get_object_or_404(Offer, id=id)
        cart.remove_quantity(offer)
        return redirect('cart:cart')


class CartView(View):

    def get(self, request):
        cart = Cart(request)

        categories = get_category()
        context = {
            'cart': cart,
            'categories': categories,

        }
        return render(request, 'cart/cart_detail.html', context)
