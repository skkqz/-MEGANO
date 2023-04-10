from django.urls import path, include
from .views import CartView, CartAdd, CartRemove, CartDelete, AddQuantity, RemoveQuantity


app_name = 'cart'


urlpatterns = [
    path('', include([
        path('cart', CartView.as_view(), name='cart'),
        path('<int:id>/add/', CartAdd.as_view(), name='cart-add'),
        path('<int:id>/remove', CartRemove.as_view(), name='cart-remove'),
        path('delete/', CartDelete.as_view(), name='cart-delete'),
        path('<int:id>/add-quantity', AddQuantity.as_view(), name='add-quantity'),
        path('<int:id>/remove-quantity', RemoveQuantity.as_view(), name='remove-quantity')
    ])),
]
