from typing import List, Tuple, Optional
from random import sample, choice, randint
import datetime
import json
import requests

from django.core.cache import cache
from django.conf import settings
from django.db.models import QuerySet, Q, Avg, Max, Count, Min
from django.http import HttpRequest
from product.models import (
    Category,
    Product,
    Banner,
    ProductImage,
    Property,
    ProductProperty,
    Offer,
    LoggingImportFileModel
)


def get_category(cache_key: str = None,
                 cache_time: int = settings.CACHE_STORAGE_TIME) -> QuerySet:
    """
    Возвращает кешированный список активных категорий.
    :param cache_key: ключ кеша.
    :param cache_time: время кеширования в секундах.
    :return:
    """
    categories = Category.objects.filter(active=True)

    if cache_key is None:
        cache_key = 'categories'

    cached_data = cache.get_or_set(cache_key, categories, cache_time)

    return cached_data


def get_queryset_for_category(request: HttpRequest) -> QuerySet:
    """
    Возвращает список продуктов в заданной категории товаров.
    Если категория не задана, возвращает список всех продуктов.
    :param request: HTTP request, в query-string которого содержится название категории товара
    :return: QuerySet
    """
    category_id = request.GET.get('category', '')

    if category_id:  # if category is passed in query-string
        queryset = Category.objects.get(id=category_id)
        cache_key = f"category:{category_id}"
        category = cache.get_or_set(cache_key, queryset, settings.CACHE_STORAGE_TIME)
        if not category.level:  # if root category, select products of full tree category
            queryset = Product.objects. \
                select_related('category'). \
                prefetch_related('seller'). \
                filter(category__tree_id=category.tree_id).all()
        else:  # if child category, select products of this category
            queryset = Product.objects. \
                select_related('category'). \
                prefetch_related('seller'). \
                filter(category=category_id).all()
    else:  # if category isn't passed in query-string
        queryset = Product.objects. \
            select_related('category').prefetch_related('seller').all()

    queryset = queryset.order_by('id')

    return queryset


def apply_filter_to_catalog(request: HttpRequest, queryset: QuerySet) -> QuerySet:
    """
    Возвращает отфильтрованный список товаров в выбранной категории товаров
    :param request: HTTP request, в query-string которого указаны параметры фильтрации
    :param queryset: список товаров в выбранной категории товаров
    :return:
    """
    # filter for price
    price = request.GET.get('price')
    if price:
        price_from, price_to = map(int, price.split(';'))
        queryset = queryset.filter(Q(offers__price__gte=price_from) &
                                   Q(offers__price__lte=price_to))

    # filter for seller
    seller = request.GET.get('seller')
    if seller:
        queryset = queryset.filter(seller__name=seller)

    # filter for title
    title = request.GET.get('title')
    if title:
        queryset = queryset.filter(name__icontains=title)

    # filter for free delivery
    delivery = request.GET.get('deliv')
    if delivery == 'on':
        queryset = queryset.filter(offers__is_free_delivery=True)

    # filter for product in stock
    stock = request.GET.get('stock')
    if stock == 'on':
        queryset = queryset.filter(offers__is_present=True)

    return queryset


def apply_sorting_to_catalog(request: HttpRequest, queryset: QuerySet) -> QuerySet:
    """
    Возвращает отсортированный список товаров в выбранной категории товаров
    :param request: HTTP request, в query-string которого указаны параметры сортировки
    :param queryset: список товаров в выбранной категории товаров
    :return:
    """
    # sorting on price
    sort_by = request.GET.get('sort', None)
    if sort_by == 'aprice':
        queryset = queryset.annotate(avg_price=Avg('offers__price')).order_by('avg_price')
    elif sort_by == 'dprice':
        queryset = queryset.annotate(avg_price=Avg('offers__price')).order_by('-avg_price')
    elif sort_by == 'arate':
        queryset = queryset.annotate(rating=Avg('offers__feedback__rating', default=0)).order_by('rating')
    elif sort_by == 'drate':
        queryset = queryset.annotate(rating=Avg('offers__feedback__rating', default=0)).order_by('-rating')
    elif sort_by == 'anew':
        queryset = queryset.annotate(date=Max('offers__added_at')).order_by('date')
    elif sort_by == 'dnew':
        queryset = queryset.annotate(date=Max('offers__added_at')).order_by('-date')
    elif sort_by == 'apop':
        queryset = queryset.annotate(count=Count('offers__order_items__offer')).order_by('count')
    elif sort_by == 'dpop':
        queryset = queryset.annotate(count=Count('offers__order_items__offer')).order_by('-count')

    queryset = queryset.annotate(avg_price=Avg('offers__price'))

    return queryset


def get_banners(qty: int = 3) -> List[Banner]:
    """
    Возвращает список из qty активных баннеров, баннеры выбираются случайным образом.
    :param qty: Количество возвращаемых баннеров. По-умолчанию, 3
    :return: Список из qty экземпляров модели Banner
    """
    banners = Banner.objects.filter(is_active=True)

    result = []
    if banners:  # делаем выборку
        # проверка, что кол-во баннеров в пределах от 1 до 3
        if qty < 1 or qty > 3:
            qty = 3
            # если в модели Banners меньше экземпляров, чем qty
        if banners.count() < qty:
            qty = banners.count()
        banners = list(banners)

        result = sample(banners, k=qty)

    return result


def get_favorite_categories(qty: int = 3,
                            cache_time: int = settings.CACHE_STORAGE_TIME) -> List[Category]:
    """
    Возвращает кешированный список из qty категорий.
    :param qty: кол-во избранных категорий, по-умолчанию, 3.
    :param cache_time: время кеширования списка.
    :return: список категорий или пустой список, если нет категорий.
    """
    categories = [category
                  for category
                  in get_category()
                  if category.is_leaf_node()]

    if not categories:
        return categories

    # если кол-во категорий меньше qty, qty = кол-ву категорий
    length = len(categories)
    if length < qty:
        qty = length

    cached_data = cache.get_or_set("favorite_categories",
                                   sample(categories, qty),
                                   cache_time)

    return cached_data


def get_min_price_in_category(category: Category) -> float:
    """
    Вычисляет минимальную стоимость товара в категории.
    :param category: категория, для которой вычисляется минимальная цена.
    :return: минимальная цена.
    """
    result = Product.objects.select_related('category').\
        filter(category_id=category.id).aggregate(min_price=Min('offers__price'))

    return result['min_price']


def get_popular_products(qty: int = 8, cache_key: str = None,
                         cache_time: int = settings.CACHE_STORAGE_TIME) -> List[dict]:
    """
    Возвращает кешированный список из qty популярных (по кол-ву продаж) товаров.
    :param qty: кол-во популярных товаров.
    :param cache_key: ключ кеша.
    :param cache_time: время, на которое кешируется список.
    :return: список популярных товаров.
    """
    if cache_key is None:
        cache_key = "popular-products"

    queryset = Product.objects.select_related('category').prefetch_related('seller').\
        annotate(count=Count('offers__order_items__offer')).\
        annotate(avg_price=Avg('offers__price')).order_by('-count')[:qty]

    cached_data = cache.get_or_set(cache_key, queryset, cache_time)

    return cached_data


def get_limited_edition(cache_time: int = settings.CACHE_STORAGE_TIME) -> \
        Tuple[Optional[dict], Optional[List[dict]]]:
    """
    Возвращает кешированный кортеж из предложения дня и списка товаров ограниченного тиража.
    :param cache_time: время, на которое кешируется список.
    :return: список популярных товаров.
    """
    # заносит текущую дату в кэш
    current_day = datetime.datetime.today().strftime("%d.%m.%Y")
    cached_date = cache.get_or_set("current_day", current_day, cache_time)

    # если наступили новые сутки, удаляем ключи
    if cached_date != current_day:
        keys = ["limited_list", "day_offer", "limited"]
        cache.delete_many(keys)
        cache.set("current_day", current_day, cache_time)

    queryset = Product.objects.select_related('category').prefetch_related('seller').\
        filter(is_limited=True).values('id', 'name', 'images__image', 'category__name'). \
        annotate(avg_price=Avg('offers__price'))

    limited_list = cache.get_or_set("limited_list", queryset, cache_time)

    # если нет достаточного кол-ва товаров ограниченного тиража
    if len(limited_list) < 2:
        return None, None

    day_offer = cache.get_or_set("day_offer", choice(limited_list), cache_time)

    limited = cache.get_or_set("limited",
                               [qs for qs in limited_list if qs != day_offer],
                               cache_time)

    return day_offer, limited


def get_object_or_none(obj, **kwargs):
    """Возвращает продукт, если его нет, то None"""

    try:
        return obj.objects.get(**kwargs)
    except obj.DoesNotExist:
        return None


def upload_product_file(file, seller, file_name):  # noqa: C901
    """Парсинг файла json и создание экземпляров модели"""

    file_read = file.read()
    file_json = json.loads(file_read)

    for i_category in file_json['category']:
        category = get_object_or_none(Category, name=i_category)

        try:
            if not category:
                category = Category.objects.create(name=i_category)
        except TypeError as ex:
            LoggingImportFileModel.objects.create(
                file_name=file_name,
                seller=seller,
                message=f'Ошибка создании Category {i_category}: {ex} | {type(ex)}'
            )
            continue

        for i_product in file_json['category'][i_category]:
            product = get_object_or_none(Product, name=i_product['name'])

            if not product:
                property = get_object_or_none(Property, name=i_product['property']['name'])
                try:
                    if not property:
                        property = Property.objects.create(name=i_product['property']['name'])
                except (KeyError, TypeError) as ex:
                    LoggingImportFileModel.objects.create(
                        file_name=file_name,
                        seller=seller,
                        message=f'Ошибка создании Property {i_product["name"]}: {ex} | {type(ex)}'
                    )
                    continue

                try:
                    product = Product.objects.create(
                                        name=i_product['name'],
                                        description=i_product['description'],
                                        category=category,
                                    )
                except (KeyError, TypeError) as ex:
                    LoggingImportFileModel.objects.create(
                        file_name=file_name,
                        seller=seller,
                        message=f'Ошибка создании Product {i_product["name"]}: {ex} | {type(ex)}'
                    )
                    continue

                try:
                    ProductProperty.objects.create(
                        product=product,
                        property=property,
                        value=i_product['property']['value']
                    )
                except (KeyError, TypeError) as ex:
                    LoggingImportFileModel.objects.create(
                        file_name=file_name,
                        seller=seller,
                        message=f'Ошибка создании ProductProperty {product}: {ex} | {type(ex)}'
                    )
                    continue

                if i_product.get('image'):
                    try:
                        for image in i_product['image']:
                            r = requests.get(image)
                            file_img_name = f'{randint(1, 9999)}_{i_product["name"]}.jpg'

                            with open(f'{settings.MEDIA_ROOT}{settings.MEDIA_IMAGE_URL}{file_img_name}', 'wb')\
                                    as image_file:
                                image_file.write(r.content)

                            ProductImage.objects.create(
                                product=product,
                                image=f'{settings.MEDIA_IMAGE_URL}{file_img_name}'
                            )
                    except (KeyError, TypeError) as ex:
                        LoggingImportFileModel.objects.create(
                            file_name=file_name,
                            seller=seller,
                            message=f'Ошибка создании ProductImage {product}: {ex} | {type(ex)}'
                        )
                        continue

            if i_product.get('offer'):
                try:
                    Offer.objects.create(
                        product=product,
                        seller=seller,
                        price=i_product['offer']['price']
                    )
                except (KeyError, TypeError) as ex:
                    LoggingImportFileModel.objects.create(
                        file_name=file_name,
                        seller=seller,
                        message=f'Ошибка создании Offer {product}: {ex} | {type(ex)}'
                    )
                    continue
    return


class BannersView:
    """Тест. Отображение баннеров"""
    template_name = 'product/banners-view.html'

    @staticmethod
    def get_banners(qty: int = 3):
        """ Возвращает список из qty активных баннеров. """
        banners = Banner.objects.filter(is_active=True)
        result = []
        if banners.exists():
            if 3 < qty < 1:
                qty = 3
            if banners.count() < qty:
                qty = banners.count()
            banners = list(banners)
            result = sample(banners, k=qty)
        return result

    def get_context_data(self, qty: int = 3, **kwargs):
        """ Добавляет в контекст список баннеров. Список кэшируется. """
        context = super().get_context_data(**kwargs)
        # заменить в ключе имя на емейл
        offers_cache_key = f'offers:{self.request.user.username}'
        # Получаем список баннеров и кэшируем его
        banner_list = self.get_banners(qty=qty)
        cached_data = cache.get_or_set(offers_cache_key, banner_list, 1 * 60)
        context['banners'] = cached_data
        return context


class ImageView:
    @staticmethod
    def get_image(product_id):
        context = ProductImage.objects.filter(product=product_id).all()
        return context
