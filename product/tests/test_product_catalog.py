from django.db.models import Avg, Count, Max
from django.test import TestCase, tag, override_settings
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

from product.models import Category, Product, Offer, Feedback
from shop.models import Seller
from orders.models import Order, OrderItem
from .test_main_page import create_orders


@tag("catalog")
@override_settings(CACHES=settings.TEST_CACHES)
class ProductCatalogViewTest(TestCase):
    """ Тесты отображения каталога товаров. """
    @classmethod
    def setUpTestData(cls):
        cls.url = '/product/catalog/'
        cls.url_name = reverse('catalog-view')

        # Создается структура таблиц БД
        # --- категории товаров
        create_category()

        # --- продавцы
        create_sellers()

        # --- товары
        create_products()

        # --- предложения
        create_offers()

        # --- заказанные товары
        create_ordered_items()

        # --- отзывы к товарам
        set__feedback()

    def test_url_exists_at_correct_location(self):
        """Тест на доступность страницы по url"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        """Тест на доступность страницы по name"""
        response = self.client.get(self.url_name)
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):
        """Тест, что страница использует заданный http-шаблон"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/product-catalog.html')

    def test_get_categories(self):
        """Тест получения активных категорий в контексте."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("categories" in response.context)
        categories = response.context["categories"]
        active_categories = Category.objects.filter(active=True)
        self.assertEqual(list(categories), list(active_categories))

    def test_get_sellers(self):
        """Тест получения списка продавцов в контексте."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("sellers" in response.context)
        sellers = response.context["sellers"]
        all_sellers = Seller.objects.all()
        self.assertEqual(list(sellers), list(all_sellers))

    def test_get_all_products_page_1(self):
        """Тест, что без указания категории, выводятся все товары.
        На странице 1 отображается заданное кол-во товаров."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # в контекст передается id категории
        self.assertTrue('current_category' in response.context)
        current_category = response.context['current_category']
        self.assertEqual(current_category, '')

        # передаются продукты
        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']

        # кол-во элементов на странице
        self.assertEqual(len(catalog), settings.CATALOG_PRODUCT_PER_PAGE)

        # есть следующая страница 2
        self.assertTrue('page_obj' in response.context)
        has_next_page = response.context['page_obj'].has_next()
        self.assertTrue(has_next_page)

    def test_get_all_products_page_2(self):
        """Тест, что без указания категории, выводятся все товары.
        На странице 1 отображается заданное кол-во товаров."""
        response = self.client.get(self.url + '?page=2')
        self.assertEqual(response.status_code, 200)

        # передаются продукты
        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']

        # кол-во элементов на странице
        number_elements = Product.objects.all().count() - settings.CATALOG_PRODUCT_PER_PAGE
        self.assertEqual(len(catalog), number_elements)

    def test_get_products_for_child_category(self):
        """Тест, что выводятся все товары для заданной категории.
        Отображается заданное кол-во товаров."""
        category = Category.objects.get(name='SSD')
        response = self.client.get(self.url + f'?category={category.id}')
        self.assertEqual(response.status_code, 200)

        # в контекст передается id категории
        self.assertTrue('current_category' in response.context)
        current_category = response.context['current_category']
        self.assertEqual(current_category, str(category.id))

        # передаются продукты
        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        products_in_category = Product.objects.filter(category_id=category.id)
        self.assertEqual(list(catalog), list(products_in_category))

    def test_calculate_avg_price(self):
        """Тест, что указывается средняя по всем продавцам цена товара."""
        category = Category.objects.get(name='SSD')
        response = self.client.get(self.url + f'?category={category.id}')
        self.assertEqual(response.status_code, 200)

        # переданные продукты
        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']

        # проверка вычисления средней цены по всем продавцам
        for i, product in enumerate(catalog, start=1):
            with self.subTest(i=i):
                price = product.avg_price
                avg = Offer.objects.filter(product_id=product.id).aggregate(avg_price=Avg('price'))
                self.assertEqual(price, avg['avg_price'])

    def test_get_products_for_parent_category(self):
        """Тест, что выводятся все товары для заданной родительской категории.
        Отображается заданное кол-во товаров."""
        category = Category.objects.get(name='Components')
        response = self.client.get(self.url + f'?category={category.id}')
        self.assertEqual(response.status_code, 200)

        # переданные товары
        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        # товары в БД
        queryset = Product.objects. \
            select_related('category'). \
            prefetch_related('seller'). \
            filter(category__tree_id=category.tree_id).all()
        self.assertEqual(list(catalog), list(queryset))

    def test_filter_by_price(self):
        """Тест фильтрации по цене."""
        category = Category.objects.get(name='Components')
        response = self.client.get(self.url + f'?category={category.id}&price=1000;1110')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        prices = [item.avg_price for item in catalog]
        min_price, max_price = min(prices), max(prices)
        self.assertTrue(min_price >= 1000)
        self.assertTrue(max_price <= 1110)

    def test_filter_by_title_with_results(self):
        """Тест фильтрации по названию, совпадения найдены."""
        category = Category.objects.get(name='Components')
        response = self.client.get(self.url + f'?category={category.id}&title=Product')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        names = [item.name for item in catalog]
        for i, name in enumerate(names):
            with self.subTest(i=i):
                self.assertIn('Product'.lower(), name)

    def test_filter_by_title_without_results(self):
        """Тест фильтрации по названию, совпадения не найдены."""
        category = Category.objects.get(name='Components')
        response = self.client.get(self.url + f'?category={category.id}&title=MSI')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        self.assertEqual(list(catalog), [])

    def test_filter_by_seller_with_results(self):
        """Тест фильтрации по продавцу, совпадения найдены."""
        category = Category.objects.get(name='Components')
        response = self.client.get(self.url + f'?category={category.id}&seller=Shop2')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        queryset = Product.objects.prefetch_related('seller').filter(seller__name='Shop2')
        self.assertEqual(list(catalog), list(queryset))

    def test_filter_by_seller_without_results(self):
        """Тест фильтрации по продавцу, совпадения не найдены."""
        category = Category.objects.get(name='Processors')
        response = self.client.get(self.url + f'?category={category.id}&seller=Shop2')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        queryset = Product.objects.select_related('category').\
            prefetch_related('seller').filter(seller__name='Shop2', category=category.id)
        self.assertEqual(list(catalog), list(queryset))

    def test_filter_by_in_stock(self):
        """Тест фильтрации по наличию в магазине."""
        category = Category.objects.get(name='Components')
        response = self.client.get(self.url + f'?category={category.id}&stock=on')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        queryset = Product.objects.select_related('category').\
            prefetch_related('seller').filter(offers__is_present=True)
        self.assertEqual(list(catalog), list(queryset))

    def test_filter_by_free_delivery(self):
        """Тест фильтрации по наличию бесплатной доставки."""
        category = Category.objects.get(name='Components')
        response = self.client.get(self.url + f'?category={category.id}&deliv=on')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        queryset = Product.objects.select_related('category').\
            prefetch_related('seller').filter(offers__is_free_delivery=True)
        self.assertEqual(list(catalog), list(queryset))

    def test_sorting_by_price_desc(self):
        """Тест сортировке по цене по убыванию."""
        category = Category.objects.get(name='Processors')
        response = self.client.get(self.url + f'?category={category.id}&sort=dprice')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        queryset = Product.objects.select_related('category'). \
            filter(category_id=category.id).annotate(avg_price=Avg('offers__price')).order_by('-avg_price')
        self.assertEqual(list(catalog), list(queryset))

    def test_sorting_by_price_asc(self):
        """Тест сортировке по цене по возрастанию."""
        category = Category.objects.get(name='Processors')
        response = self.client.get(self.url + f'?category={category.id}&sort=aprice')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        queryset = Product.objects.select_related('category'). \
            filter(category_id=category.id).annotate(avg_price=Avg('offers__price')).order_by('avg_price')
        self.assertEqual(list(catalog), list(queryset))

    def test_sorting_by_popularity_desc(self):
        """Тест сортировке по популярности по убыванию."""
        category = Category.objects.get(name='Processors')
        response = self.client.get(self.url + f'?category={category.id}&sort=dpop')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        queryset = Product.objects.select_related('category'). \
            filter(category_id=category.id).annotate(count=Count('offers__order_items__offer')).\
            order_by('-count')
        self.assertEqual(list(catalog), list(queryset))

    def test_sorting_by_popularity_asc(self):
        """Тест сортировке по популярности по возрастанию."""
        category = Category.objects.get(name='Processors')
        response = self.client.get(self.url + f'?category={category.id}&sort=apop')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        queryset = Product.objects.select_related('category'). \
            filter(category_id=category.id).annotate(count=Count('offers__order_items__offer')).\
            order_by('count')
        self.assertEqual(list(catalog), list(queryset))

    def test_sorting_by_novelty_desc(self):
        """Тест сортировке по новизне по убыванию."""
        category = Category.objects.get(name='Processors')
        response = self.client.get(self.url + f'?category={category.id}&sort=dnew')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        queryset = Product.objects.select_related('category'). \
            filter(category_id=category.id).annotate(date=Max('offers__added_at')).\
            order_by('-date')
        self.assertEqual(list(catalog), list(queryset))

    def test_sorting_by_novelty_asc(self):
        """Тест сортировке по новизне по убыванию."""
        category = Category.objects.get(name='Processors')
        response = self.client.get(self.url + f'?category={category.id}&sort=anew')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        queryset = Product.objects.select_related('category'). \
            filter(category_id=category.id).annotate(date=Max('offers__added_at')).\
            order_by('date')
        self.assertEqual(list(catalog), list(queryset))

    def test_sorting_by_rating_desc(self):
        """Тест сортировке по рейтингу по убыванию."""
        category = Category.objects.get(name='Processors')
        response = self.client.get(self.url + f'?category={category.id}&sort=drate')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        queryset = Product.objects.select_related('category'). \
            filter(category_id=category.id).annotate(rating=Avg('offers__feedback__rating', default=0)).\
            order_by('-rating')
        self.assertEqual(list(catalog), list(queryset))

    def test_sorting_by_rating_asc(self):
        """Тест сортировке по рейтингу по возрастанию."""
        category = Category.objects.get(name='Processors')
        response = self.client.get(self.url + f'?category={category.id}&sort=arate')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('catalog' in response.context)
        catalog = response.context['catalog']
        queryset = Product.objects.select_related('category'). \
            filter(category_id=category.id).annotate(rating=Avg('offers__feedback__rating', default=0)).\
            order_by('rating')
        self.assertEqual(list(catalog), list(queryset))


# ====== Методы для формирования таблиц БД


def create_category():
    """Создаются категории: 3 родительских, 2 дочерних, 4 активных, 1 родительская неактивная"""
    Category.objects.create(name='Tablets', active=True)
    category = Category.objects.create(name='Components', active=True)
    Category.objects.create(name="SSD", parent=category, active=True)
    Category.objects.create(name="Processors", parent=category, active=True)
    Category.objects.create(name='Appliances', active=False)


def create_sellers():
    """Создает продавца"""
    user_1 = get_user_model().objects.create_user(password='test1234',
                                                  email='test1@test.ru',
                                                  phone="9787470001")
    Seller.objects.create(user=user_1, name='Shop1', description='test1',
                          address='test', number=1234567890)
    user_2 = get_user_model().objects.create_user(password='test1234tests',
                                                  email='test1@mail.ru',
                                                  phone="9787470002")
    Seller.objects.create(user=user_2, name='Shop2', description='test1',
                          address='test', number=1234567890)


def create_products():
    """Создает товары."""
    category_1 = Category.objects.get(name="SSD")
    category_2 = Category.objects.get(name="Processors")
    category_3 = Category.objects.get(name="Tablets")

    products_1 = [Product(name=f'product {i}',
                          description=f'product {i} description',
                          category=category_1,
                          is_limited=True)
                  for i in range(1, 4)]

    products_2 = [Product(name=f'product {i}',
                          description=f'product {i} description',
                          category=category_2,
                          is_limited=True)
                  for i in range(4, 7)]

    products_3 = [Product(name=f'product {i}',
                          description=f'product {i} description',
                          category=category_3)
                  for i in range(7, 10)]

    products_1.extend(products_2)
    products_1.extend(products_3)

    Product.objects.bulk_create(products_1)


def create_offers():
    """Создает предложения у двух продавцов."""
    seller = Seller.objects.first()
    products = Product.objects.all()
    offers = [Offer(product=product,
                    seller=seller,
                    price=1000+i*10,
                    is_present=False,
                    is_free_delivery=False)
              for i, product
              in enumerate(products)]

    Offer.objects.bulk_create(offers)

    seller = Seller.objects.last()
    category = Category.objects.get(name='SSD')
    products = Product.objects.filter(category_id=category.id)
    offers = [Offer(product=product,
                    seller=seller,
                    price=1200 + i * 10)
              for i, product
              in enumerate(products)]

    Offer.objects.bulk_create(offers)


def set__feedback():
    """Добавляет отзывы."""
    # Рейтинг: Product 5 = 5, Product 4 = 4.5, Product 6 = 4
    # пользователи
    user_1 = get_user_model().objects.first()
    user_2 = get_user_model().objects.last()

    # товары
    offers = Offer.objects.filter(product__category__name='Processors')
    product_1 = offers[0]
    product_2 = offers[1]
    product_3 = offers[2]

    # отзывы
    feedbacks = [
        Feedback(
            author=user_1,
            offer=product_1,
            rating=5,
            description='test'
        ),
        Feedback(
            author=user_1,
            offer=product_2,
            rating=5,
            description='test'
        ),
        Feedback(
            author=user_1,
            offer=product_3,
            rating=5,
            description='test'
        ),
        Feedback(
            author=user_2,
            offer=product_1,
            rating=4,
            description='test'
        ),
        Feedback(
            author=user_2,
            offer=product_2,
            rating=5,
            description='test'
        ),
        Feedback(
            author=user_2,
            offer=product_3,
            rating=3,
            description='test'
        ),
    ]

    Feedback.objects.bulk_create(feedbacks)


def create_ordered_items():
    # Создаем 3 заказа.
    # Повторяемость в заказах: Product 5, Product 4, Product 6
    create_orders()
    """Созадет товары в заказах."""
    offers = Offer.objects.filter(product__category__name='Processors')
    product_1 = offers[0]
    product_2 = offers[1]
    product_3 = offers[2]

    orders = Order.objects.all()
    order_1 = orders[0]
    order_2 = orders[1]
    order_3 = orders[2]

    ordered_items = [
        OrderItem(
            order=order_1,
            offer=product_1,
            price=1000.00,
            quantity=1
        ),
        OrderItem(
            order=order_1,
            offer=product_2,
            price=2000.00,
            quantity=1
        ),
        OrderItem(
            order=order_1,
            offer=product_3,
            price=3000.00,
            quantity=1
        ),
        OrderItem(
            order=order_2,
            offer=product_1,
            price=1100.00,
            quantity=1
        ),
        OrderItem(
            order=order_2,
            offer=product_2,
            price=2100.00,
            quantity=1
        ),
        OrderItem(
            order=order_3,
            offer=product_2,
            price=2200.00,
            quantity=1
        ),
    ]
    OrderItem.objects.bulk_create(ordered_items)
