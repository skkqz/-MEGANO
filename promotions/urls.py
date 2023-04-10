from django.urls import path
from promotions.views import PromoListView, PromoDetailView


app_name = 'promotions'
urlpatterns = [
    path('promo/', PromoListView.as_view(), name='promo-list'),
    path('promo/<int:pk>/', PromoDetailView.as_view(), name='promo-detail'),
]
