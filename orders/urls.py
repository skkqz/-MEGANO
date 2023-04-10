from django.urls import path
from orders import views

urlpatterns = [
    path('history/', views.HistoryOrderView.as_view(), name='history'),
    path('history<int:pk>/', views.HistoryOrderDetailView.as_view(), name='history-detail'),
    path('create/', views.order_create, name='order_create'),
    path('create/delivery/', views.order_create_delivery, name='order_create_delivery'),
    path('create/type-payment/', views.order_type_payment, name='order_type_payment'),
    path('create/payment/', views.order_create_payment, name='order_create_payment'),
    path('wait-payment/<int:pk>/', views.wait_payment, name='wait-payment'),
    path('create/comment/', views.order_create_comment, name='order_create_comment'),
]
