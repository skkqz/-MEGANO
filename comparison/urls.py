from django.urls import path, include
from .views import Comparison, ComparisonAdd, ComparisonRemove, ComparisonDelete

app_name = 'comparison'

urlpatterns = [
    path('', include([
        path('disp', Comparison.as_view(), name='comparison'),
        path('<id>/add/', ComparisonAdd.as_view(), name='comparison-add'),
        path('<id>/remove', ComparisonRemove.as_view(), name='comparison-remove'),
        path('delete/', ComparisonDelete.as_view(), name='comparison-delete')

    ])),
]
