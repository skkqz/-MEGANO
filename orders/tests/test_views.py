from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from orders.models import Order, OrderItem
from product.models import Product, Offer
from shop.models import Seller
from cart.service import Cart


class HistoryTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(email='test@test.ru', password='12345', phone='1111111111')
        user2 = get_user_model().objects.create_user(email='test2@test.ru', password='123452', phone='2222222222')
        seller = Seller.objects.create(user=user2, name='test2', description='test1',
                                       address='test', number=1234567)
        product = Product.objects.create(name='test', description='test')
        offer = Offer.objects.create(product=product, seller=seller, price=10.10)
        order = Order.objects.create(first_name='test', last_name='test', email='test@test.ru',
                                     address='test', number=7654321, city='test',
                                     delivery='D', status='W')
        OrderItem.objects.create(order=order, offer=offer, price=10.10)

    def setUp(self) -> None:
        self.client.login(email=self.user.email, password=self.user.password)

    def test_history(self):
        url = reverse('history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('orders/history_order.html', response.template_name)

    def test_history_detail(self):
        url = reverse('history-detail', kwargs={'pk': Order.objects.get(first_name='test').id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('orders/history_order_detail.html', response.template_name)

    def test_order_create(self):
        url = reverse('order_create')
        data = {'first_name': 'test', 'last_name': 'test', 'email': 'new_test@test.text',
                'number': 7654321, 'password1': 'test12345', 'password2': 'test12345'}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_order_create_delivery(self):
        url = reverse('order_create_delivery')
        data = {'delivery': 'A', 'city': 'test', 'address': 'test'}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_order_type_payment(self):
        url = reverse('order_type_payment')
        data = {'payment': 'C'}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_order_comment(self):
        url = reverse('order_create_comment')
        data = {'comment': 'test'}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_order_create_payment(self):
        offer = Offer.objects.get(price=10.10)
        url = reverse('order_create_payment')
        response = self.client.get(url)
        request = response.wsgi_request
        cart = Cart(request)
        cart.add(offer, quantity=3)
        cart.save()
        print(cart.cart)
        data = {'card_number': '12345678'}
        orders_before = Order.objects.all().count()
        print(OrderItem.objects.first().quantity)
        response = self.client.post(url, data=data, follow=True)
        print(OrderItem.objects.first().quantity)
        orders_after = Order.objects.all().count()
        self.assertEqual(orders_after - orders_before, 1)
        self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        order_item = OrderItem.objects.get(price=10.10)
        order_item.delete()
        order = Order.objects.get(number=7654321)
        order.delete()
        offer = Offer.objects.get(price=10.10)
        offer.delete()
        product = Product.objects.get(name='test')
        product.delete()
        seller = Seller.objects.get(name='test2')
        seller.delete()
        user = get_user_model().objects.get(email='test@test.ru')
        user.delete()
        super().tearDownClass()
