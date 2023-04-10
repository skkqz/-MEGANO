from django.contrib.auth import get_user_model
from django.test import TestCase, tag, override_settings
from django.urls import reverse
from django.conf import settings
from product.models import Category, Product, Offer, Banner
from shop.models import Seller
from orders.models import Order, OrderItem


@tag("main-page")
@override_settings(CACHES=settings.TEST_CACHES)
class MainPageViewTest(TestCase):
    """ Тесты отображения главной страницы. """
    @classmethod
    def setUpTestData(cls):
        cls.url = '/'
        cls.url_name = reverse('main-page')

        # Создаем структуру таблиц
        # --- категории товаров
        create_category()

        # --- продавец
        create_sellers()

        # --- товары
        create_products()

        # --- предложения
        create_offers()

        # --- баннеры
        create_banners()

        # --- заказы
        create_orders()

        # --- заказанные товары
        create_ordered_items()

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
        self.assertTemplateUsed(response, 'product/index-2.html')

    def test_get_category(self):
        """Тест получения списка активных категорий длиной 3."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("categories" in response.context)
        categories = response.context['categories']
        count = Category.objects.filter(active=True).count()
        count_in_context = len(categories)
        self.assertEqual(count_in_context, count)

    def test_get_banners(self):
        """Тест, что получает список активных баннеров длиной 3."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("banners" in response.context)
        banners = response.context['banners']
        self.assertEqual(len(banners), 3)

    @staticmethod
    def update_banner_activity():
        """Делает все баннеры неактивными."""
        banners = Banner.objects.all()
        for banner in banners:
            banner.is_active = False
        Banner.objects.bulk_update(banners, ['is_active'])

    def test_get_banners_empty(self):
        """Тест отработки пустого списка баннеров."""
        self.update_banner_activity()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("banners" in response.context)
        banners = response.context['banners']
        self.assertEqual(len(banners), 0)

    def test_get_one_banners(self):
        """Тест, что получает меньше трех активных баннеров."""
        # делаем один активный баннер
        self.update_banner_activity()
        banner = Banner.objects.first()
        banner.is_active = True
        banner.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("banners" in response.context)
        banners = response.context['banners']
        self.assertEqual(len(banners), 1)

    def test_get_favorite_categories(self):
        """Тест, что получает список избранных категорий длиной 3."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("favorite" in response.context)
        favorite = response.context['favorite']
        self.assertEqual(len(favorite), 3)
        # проверка, что выбраны только category.is_leaf_node()
        wrong_category = Category.objects.get(name="category_2")
        self.assertNotIn(wrong_category, favorite)

    def test_get_popular_products(self):
        """Тест, что получает список популярных товаров."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("popular" in response.context)
        popular = response.context['popular']
        # список отсортирован по кол-ву продаж
        self.assertEqual(popular[0].name, 'product 2')
        self.assertEqual(popular[1].name, 'product 1')
        self.assertEqual(popular[2].name, 'product 3')

    def test_get_day_offer(self):
        """Тест на получения товара дня."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("day_offer" in response.context)
        day_offer = response.context['day_offer']
        self.assertTrue("limited" in response.context)
        limited = response.context['limited']
        # предложение дня не в списке ограниченного тиража
        self.assertNotIn(day_offer, limited)

    def test_get_limited_edition(self):
        """Тест на получения товаров ограниченный тираж."""
        full_limited = Product.objects.filter(is_limited=True).values('name')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("limited" in response.context)
        limited = response.context['limited']
        # проверка, что в списке только товары со свойством is_limited=True
        selected_limited = [{'name': item['name']} for item in limited]
        for item in selected_limited:
            self.assertIn(item, full_limited)


def create_category():
    """Создаются категории: 3 родительских, 2 дочерних, 4 активных, 1 родительская неактивная"""
    Category.objects.create(name='category_1', active=True)
    category = Category.objects.create(name='category_2', active=True)
    Category.objects.create(name="category_2_1", parent=category, active=True)
    Category.objects.create(name="category_2_2", parent=category, active=True)
    Category.objects.create(name='category_3', active=False)


def create_sellers():
    """Создает продавца"""
    user = get_user_model().objects.create_user(password='test1234',
                                                email='test1@test.ru')
    Seller.objects.create(user=user, name='seller', description='test1',
                          address='test', number=1234567890)


def create_products():
    """Создает товары"""
    category_21 = Category.objects.get(name="category_2_1")
    category_22 = Category.objects.get(name="category_2_2")

    products_1 = [Product(name=f'product {i}',
                          description=f'product {i} description',
                          category=category_21,
                          is_limited=True)
                  for i in range(1, 4)]

    products_2 = [Product(name=f'product {i}',
                          description=f'product {i} description',
                          category=category_22)
                  for i in range(4, 10)]
    products_1.extend(products_2)

    Product.objects.bulk_create(products_1)


def create_offers():
    seller = Seller.objects.first()
    products = Product.objects.all()
    offers = [Offer(product=product,
                    seller=seller,
                    price=1000+i)
              for i, product
              in enumerate(products)]
    Offer.objects.bulk_create(offers)


def create_banners():
    """Создает баннеры."""
    products = Product.objects.all()
    banners = [Banner(title=f"banner_{i}",
                      brief=f"description_{i}",
                      product=product,
                      is_active=True)
               for i, product
               in enumerate(products, start=1)
               ]
    Banner.objects.bulk_create(banners)


def create_orders():
    """Создаем заказы."""
    orders = [
        Order(
              first_name="Elon",
              last_name="Musk",
              email="e.musk@yandex.ru",
              address="santa barbara",
              number="100001",
        ),
        Order(
            first_name="Elon",
            last_name="Musk",
            email="e.musk@yandex.ru",
            address="santa barbara",
            number="100001",
        ),
        Order(
            first_name="Elon",
            last_name="Musk",
            email="e.musk@yandex.ru",
            address="santa barbara",
            number="100001",
        ),
    ]
    Order.objects.bulk_create(orders)


def create_ordered_items():
    """Созадет товары в заказах."""
    product_1 = Offer.objects.get(product__name="product 1")
    product_2 = Offer.objects.get(product__name="product 2")
    product_3 = Offer.objects.get(product__name="product 3")

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
