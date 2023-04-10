from django.urls import path
# from product.services import BannersView
from product.views import (
    ProductDetailView,
    CategoryView,
    FeedbackDetailView,
    HistoryViewsView,
    ProductCatalogView,
    UploadProductFileView
)


urlpatterns = [
    # path('banners/', BannersView.as_view(), name='banners'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('category/', CategoryView.as_view(), name='category'),
    path('offer/<int:pk>/', FeedbackDetailView.as_view(), name='offer-detail'),
    path('catalog/', ProductCatalogView.as_view(), name='catalog-view'),
    path('history_view/', HistoryViewsView.as_view(), name='history_view'),
    path('upload_file/', UploadProductFileView.as_view(), name='upload_file'),
]
