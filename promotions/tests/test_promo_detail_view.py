from django.contrib.auth import get_user_model
from django.test import TestCase, tag, override_settings
from django.urls import reverse
from django.utils import timezone
from promotions.models import PromoType, Promo, Promo2Product
from product.models import Product, Category, Offer
from shop.models import Seller
from django.conf import settings


@tag('promo-detail')
@override_settings(CACHES=settings.TEST_CACHES)
class PromoDetailViewTest(TestCase):
    """ Тесты отображения детальной страницы акции. """

    @classmethod
    def setUpTestData(cls):
        # создаём акцию
        promo_type_1 = PromoType.objects.create(name='promo type 1', code=10)
        promo = Promo.objects.create(name='promo 1',
                                     promo_type=promo_type_1,
                                     description='description',
                                     finished=timezone.now(),
                                     is_active=True)
        # создаём продукты и привязываем их к акции
        user = get_user_model().objects.create_user(password='test1234',
                                                    email='test1@test.ru')
        seller = Seller.objects.create(user=user, name='test1', description='test1',
                                       address='test', number=1234567890)
        category = Category.objects.create(name='test', active=True)
        for i in range(1, 7):
            product = Product.objects.create(name=f'product {i}',
                                             description=f'product {i} description',
                                             category=category)
            Offer.objects.create(product=product, seller=seller, price=1000+i)
        # urls
        cls.pk = promo.id
        cls.url = f'/promos/promo/{promo.id}/'
        cls.url_name = reverse('promotions:promo-detail', args=[promo.id])

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
        self.assertTemplateUsed(response, 'promotions/promo-detail.html')

    def test_template_takes_content(self):
        """Тест на передачу в шаблон контекста"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # контекст
        self.assertTrue('categories' in response.context)
        self.assertTrue('promo' in response.context)
        self.assertTrue('page_obj' in response.context)
        # содержимое контекста
        category_count = Category.objects.filter(active=True).count()
        self.assertEqual(len(response.context['categories']), category_count)
        promo_name = Promo.objects.first().name
        self.assertEqual(response.context['promo'].name, promo_name)

    def test_pagination_first_page(self):
        """Тест, что пагинатор получает все товары из каталога и
        передает заданное кол-во на страницу 1"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('page_obj' in response.context)
        # есть следующая страница 2
        has_next_page = response.context['page_obj'].has_next()
        self.assertTrue(has_next_page)
        next_page_number = response.context['page_obj'].next_page_number()
        self.assertEqual(next_page_number, 2)
        # кол-во элементов на странице
        product_list = response.context['page_obj'].object_list
        self.assertEqual(len(product_list), settings.PROMO_PRODUCTS_PER_PAGE)

    def test_pagination_second_page(self):
        """Тест, что пагинатор получает все товары из каталога и
        передает оставшееся кол-во на страницу 2"""
        response = self.client.get(self.url + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('page_obj' in response.context)
        # нет следующей страницы
        has_next_page = response.context['page_obj'].has_next()
        self.assertFalse(has_next_page)
        # есть предыдущая страница 1
        has_previous_page = response.context['page_obj'].has_previous()
        self.assertTrue(has_previous_page)
        previous_page_number = response.context['page_obj'].previous_page_number()
        self.assertEqual(previous_page_number, 1)
        # кол-во элементов на странице
        number_elements = Product.objects.all().count() - settings.PROMO_PRODUCTS_PER_PAGE
        product_list = response.context['page_obj'].object_list
        self.assertEqual(len(product_list), number_elements)

    def test_correct_product_list(self):
        """Тест, что передаются только товары, связанные с акцией"""
        # привязываем к акции два товара
        product_1 = Product.objects.first()
        product_2 = Product.objects.last()
        promo = Promo.objects.first()
        promo2product = Promo2Product.objects.create(promo=promo)
        promo2product.product.add(product_1)
        promo2product.product.add(product_2)
        products_in_promo = Promo2Product.objects.first().product.all()
        # запрос
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # есть контекст
        self.assertTrue('page_obj' in response.context)
        # кол-во элементов на странице
        product_list = response.context['page_obj'].object_list
        self.assertEqual(len(product_list), len(products_in_promo))
