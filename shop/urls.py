from django.urls import path
from .views import SellerInfo, SiteSettingsView, AccauntEditView, AccauntView

urlpatterns = [
    path('seller/<int:pk>', SellerInfo.as_view(), name='seller-info'),
    path('settings', SiteSettingsView.as_view(), name='settings'),
    path('accaunt', AccauntView.as_view(), name='accaunt'),
    path('accaunt_edit', AccauntEditView.as_view(), name='accaunt_edit'),
]
