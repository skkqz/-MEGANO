from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import QuerySet, Avg
from django.core.cache import cache
from django.http import HttpRequest
from product.models import Product
from promotions.models import Promo


def get_active_promotions(cache_key: str = None,
                          cache_time: int = settings.CACHE_STORAGE_TIME) -> QuerySet:
    """
    Возвращает кэшированный список активных акций
    :param cache_key: ключ кеша
    :param cache_time: время кэширования в секундах
    :return:
    """
    promotions = Promo.objects.filter(is_active=True)

    if cache_key is None:
        cache_key = 'promotions'
    cached_data = cache.get_or_set(cache_key, promotions, cache_time)

    return cached_data


def get_related_products(obj, request: HttpRequest, cache_key: str = None,
                         cache_time: int = settings.CACHE_STORAGE_TIME):
    """
    Возвращает кэшированный список продуктов, связанных с акцией
    :param obj: экземпляр модели акции
    :param request: Http request
    :param cache_key: ключ кеша
    :param cache_time: время кэширования в секундах
    :return:
    """
    if cache_key is None:
        cache_key = f'product_in_{obj.id}'

    product_list = obj.promo2products.first()
    if hasattr(product_list, 'product'):
        product_list = product_list.product. \
            select_related('category')
    else:
        product_list = Product.objects.\
            select_related('category')

    product_list = product_list.annotate(avg_price=Avg('offers__price')).order_by('id')

    cached_products = cache.get_or_set(cache_key, product_list, cache_time)

    promo_product_per_page = request.session.get(settings.ADMIN_SETTINGS_ID)
    if promo_product_per_page is None or promo_product_per_page.get('PROMO_PRODUCTS_PER_PAGE') is None:
        count_per_page = settings.PROMO_PRODUCTS_PER_PAGE
    else:
        count_per_page = promo_product_per_page['PROMO_PRODUCTS_PER_PAGE']

    paginator = Paginator(cached_products, count_per_page)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    return products
