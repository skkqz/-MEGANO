from django.test import TestCase
from django.conf import settings
from users.models import CustomUser


class TestCart(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(email='test@test.ru', password='12345')

    def setUp(self) -> None:
        self.session = self.client.session
        self.session[settings.CART_SESSION_ID] = []
        self.client.login(email=self.user.email, password=self.user.password)

    def test_cart_get(self):
        response = self.client.get('/cart/cart')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.session[settings.CART_SESSION_ID]), 0)

    def test_cart_add(self):
        data = {'quantity': 1, 'price': '100'}
        self.session[settings.CART_SESSION_ID].append(data)
        self.client.get('/cart/1/add')
        self.assertEqual(len(self.session[settings.CART_SESSION_ID]), 1)
        self.assertEqual(self.session[settings.CART_SESSION_ID][0]['quantity'], 1)
        self.assertEqual(self.session[settings.CART_SESSION_ID][0]['price'], '100')
