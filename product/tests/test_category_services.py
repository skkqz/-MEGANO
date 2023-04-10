from django.test import TestCase, tag, override_settings
from django.urls import reverse
from django.conf import settings
from product.models import Category


@tag("category")
@override_settings(CACHES=settings.TEST_CACHES)
class CategoryServicesTest(TestCase):
    """ Тесты сервисов получения категорий и избранных категорий. """
    @classmethod
    def setUpTestData(cls):
        cls.url = '/'
        cls.url_name = reverse('main-page')

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

    def test_get_category_empty(self):
        """ Тест, если не создано категорий или нет активных категорий. """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("categories" in response.context)
        categories = response.context['categories']
        count_in_context = len(categories)
        self.assertEqual(count_in_context, 0)

    def test_get_favorite_category_empty(self):
        """ Тест, если не создано категорий или нет активных категорий. """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("favorite" in response.context)
        categories = response.context['favorite']
        count_in_context = len(categories)
        self.assertEqual(count_in_context, 0)

    def test_get_one_category(self):
        """ Тест, если создано меньше трех категорий. """
        Category.objects.create(name='category_1', active=True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("categories" in response.context)
        categories = response.context['categories']
        count_in_context = len(categories)
        self.assertEqual(count_in_context, 1)

    def test_get_one_favorite_category(self):
        """ Тест, если создано меньше трех категорий. """
        Category.objects.create(name='category_1', active=True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("favorite" in response.context)
        categories = response.context['favorite']
        count_in_context = len(categories)
        self.assertEqual(count_in_context, 1)
