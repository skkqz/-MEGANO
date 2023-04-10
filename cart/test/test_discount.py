from decimal import Decimal
from typing import Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag, RequestFactory
from django.conf import settings
from django.utils import timezone

from product.models import Category, Product, Offer
from promotions.models import PromoType, Promo, Promo2Product
from shop.models import Seller
from users.models import CustomUser
from cart.service import Cart


@tag('discount')
class DiscountInCartTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(email='test@test.ru', password='12345', phone='9787470000')

        # Создается структура таблиц БД
        # --- категории товаров
        create_category()

        # --- продавцы
        create_sellers()

        # --- товары
        create_products()

        # --- предложения
        create_offers()

        # --- акции
        create_promotions()

    def setUp(self) -> None:
        session = self.client.session
        session[settings.CART_SESSION_ID] = []
        factory = RequestFactory()
        request = factory.get('/cart/cart')
        request.session = session
        self.cart = Cart(request)

    def test_cart_create(self):
        """Проверка создания корзины."""
        self.assertIsInstance(self.cart, Cart)

    def test_discount_on_product(self):
        """Проверка расчета скидки на товар, если задана фиксированная сумма скидки."""
        offer = Offer.objects.select_related('product').get(product__name='apple')
        # активируем акцию
        promo = promo_activate(name='product fix discount')
        # вычисление скидки при 1 и 2 штуках товара
        for i in range(2):
            with self.subTest(i=i+1):
                # добавляем товары в корзину
                self.cart.add(offer, quantity=1)
                # вычисляем скидку и сумму к оплате
                discount = self.cart.total_discount()
                due = self.cart.due()
                for_due = self.cart.get_total_price() - discount
                promo_discount = promo.fix_discount * (i + 1)
                self.assertEqual(discount, promo_discount)
                self.assertEqual(due, for_due)

    def test_discount_on_product_2(self):
        """Проверка расчета скидки на товар, если задана скидка в процентах."""
        offer = Offer.objects.select_related('product').get(product__name='apple')
        # активируем акцию
        promo = promo_activate(name='product discount')
        # вычисление скидки при 1 и 2 штуках товара
        for i in range(2):
            with self.subTest(i=i + 1):
                # добавляем товары в корзину
                self.cart.add(offer, quantity=1)
                # вычисляем скидку и сумму к оплате
                discount = self.cart.total_discount()
                due = self.cart.due()
                for_due = self.cart.get_total_price() - discount
                qty = self.cart.cart[str(offer.id)]["quantity"]
                promo_discount = offer.price * promo.discount / 100 * qty
                self.assertEqual(discount, promo_discount)
                self.assertEqual(due, for_due)

    def test_discount_on_product_3(self):
        """Проверка расчета приоритетной скидки на товар."""
        offer = Offer.objects.select_related('product').get(product__name='apple')
        # активируем акцию
        promo_1 = promo_activate(name='product discount')
        promo_2 = promo_activate(name='product fix discount')

        # добавляем 1 товар в корзину
        self.cart.add(offer, quantity=1)
        # вычисляем скидку и сумму к оплате
        discount = self.cart.total_discount()
        promo_discount = max([
            offer.price * promo_1.discount / 100,
            promo_2.fix_discount
        ])
        due = self.cart.due()
        for_due = self.cart.get_total_price() - discount
        self.assertEqual(discount, promo_discount)
        self.assertEqual(due, for_due)

    def test_discount_on_plus_one(self):
        """Проверка расчета скидки на акцию 1+1."""
        offer = Offer.objects.select_related('product').get(product__name='melon')
        # активируем акцию
        promo = promo_activate(name='promo 1+1')
        for i in range(1, 5):
            with self.subTest(i=i):
                # добавляем 1 товар в корзину
                self.cart.add(offer, quantity=1)
                # вычисляем скидку и сумму к оплате
                discount = self.cart.total_discount()
                due = self.cart.due()
                qty = self.cart.cart[str(offer.id)]["quantity"]
                promo_discount = (qty // (promo.quantity + 1)) * offer.price
                for_due = self.cart.get_total_price() - discount
                self.assertEqual(discount, promo_discount)
                self.assertEqual(due, for_due)

    def test_discount_on_plus_one_2(self):
        """Проверка расчета скидки на акцию 2+1."""
        offer = Offer.objects.select_related('product').get(product__name='melon')
        # активируем акцию
        promo = promo_activate(name='promo 2+1')
        # добавляем 1 товар в корзину
        self.cart.add(offer, quantity=1)

        for i in range(1, 6):
            with self.subTest(i=i):
                # добавляем 1 товар в корзину
                self.cart.add(offer, quantity=1)
                # вычисляем скидку и сумму к оплате
                discount = self.cart.total_discount()
                due = self.cart.due()
                qty = self.cart.cart[str(offer.id)]["quantity"]
                promo_discount = (qty // (promo.quantity + 1)) * offer.price
                for_due = self.cart.get_total_price() - discount
                self.assertEqual(discount, promo_discount)
                self.assertEqual(due, for_due)

    def test_discount_on_amount(self):
        """Проверка расчета скидки на N единиц товара."""
        offer = Offer.objects.select_related('product').get(product__name='apple')
        # активируем акцию
        promo = promo_activate(name='amount discount')

        for i in range(1, 12):
            with self.subTest(i=i):
                # добавляем 1 товар в корзину
                self.cart.add(offer, quantity=1)
                # вычисляем скидку и сумму к оплате
                discount = self.cart.total_discount()
                due = self.cart.due()
                qty = self.cart.cart[str(offer.id)]["quantity"]
                if qty >= promo.quantity:
                    promo_discount = qty * promo.discount * offer.price / 100
                else:
                    promo_discount = Decimal(0)
                for_due = self.cart.get_total_price() - discount
                self.assertEqual(discount, promo_discount)
                self.assertEqual(due, for_due)

    def test_discount_on_amount_2(self):
        """Проверка расчета скидки на N единиц товара, при фиксированной скидке."""
        offer = Offer.objects.select_related('product').get(product__name='apple')
        # активируем акцию
        promo = promo_activate(name='amount fix discount')

        for i in range(1, 12):
            with self.subTest(i=i):
                # добавляем 1 товар в корзину
                self.cart.add(offer, quantity=1)
                # вычисляем скидку и сумму к оплате
                discount = self.cart.total_discount()
                due = self.cart.due()
                qty = self.cart.cart[str(offer.id)]["quantity"]
                if qty >= promo.quantity:
                    promo_discount = promo.fix_discount
                else:
                    promo_discount = Decimal(0)
                for_due = self.cart.get_total_price() - discount
                self.assertEqual(discount, promo_discount, promo_discount)
                self.assertEqual(due, for_due)

    def test_priority_discount_on_amount(self):
        """Проверка расчета приоритетной скидки на N единиц товара."""
        offer = Offer.objects.select_related('product').get(product__name='apple')
        # активируем акции
        promo_1 = promo_activate(name='amount fix discount')
        promo_2 = promo_activate(name='amount discount')

        # при данных условиях акций при покупке менее штук 19 товаров
        # скидка составит 100 р, а более 21 цена * кол-во * %
        for i in range(1, 5):
            with self.subTest(i=i):
                # добавляем товары в корзину
                if i == 1:
                    self.cart.add(offer, quantity=10)
                    promo_discount = promo_1.fix_discount
                elif i == 2:
                    self.cart.add(offer, quantity=10)
                    promo_discount = promo_1.fix_discount
                elif i > 2:
                    self.cart.add(offer, quantity=1)
                    qty = self.cart.cart[str(offer.id)]["quantity"]
                    promo_discount = qty * promo_2.discount * offer.price / 100
                # вычисляем скидку и сумму к оплате
                discount = self.cart.total_discount()
                due = self.cart.due()
                for_due = self.cart.get_total_price() - discount
                self.assertEqual(discount, promo_discount, promo_discount)
                self.assertEqual(due, for_due)

    def test_priority_discount_in_diffrent_promos(self):
        """Проверка расчета приоритетной скидки по двум типам акций:
        % на товар и % на покупку N единиц товара."""
        offer = Offer.objects.select_related('product').get(product__name='apple')
        # активируем акции
        promo_1 = promo_activate(name='product discount')
        promo_2 = promo_activate(name='amount discount')
        promo_2.quantity = 5
        promo_2.save()

        # при покупке 5 и более товаров должна действовать скидка
        # 10%? менее 5 - 5%
        for i in range(1, 7):
            with self.subTest(i=i):
                # добавляем товары в корзину
                self.cart.add(offer, quantity=1)
                qty = self.cart.cart[str(offer.id)]["quantity"]
                if qty < promo_2.quantity:
                    promo_discount = qty * promo_1.discount * offer.price / 100
                else:
                    promo_discount = qty * promo_2.discount * offer.price / 100
                # вычисляем скидку и сумму к оплате
                discount = self.cart.total_discount()
                due = self.cart.due()
                for_due = self.cart.get_total_price() - discount
                self.assertEqual(discount, promo_discount, promo_discount)
                self.assertEqual(due, for_due)

    def test_discount_on_cart(self):
        """Проверка расчета скидки на все товары в корзине."""
        offers = Offer.objects.select_related('product').all().order_by('id')
        melon = Offer.objects.select_related('product').get(product__name='melon')
        # активируем акцию
        promo = promo_activate(name='cart')
        # проверка 3х условий: меньше 5 наименований, сумма меньше, скидки нет
        for i in range(1, 5):
            with self.subTest(i=i):
                # 4 товара, сумма меньше 1000
                if i == 1:
                    # добавляем 4 товара в корзину
                    for offer in offers[1:]:
                        self.cart.add(offer, quantity=1)
                        promo_discount = Decimal(0)

                # 4 товара, сумма больше 1000
                elif i == 2:
                    # добавляем 2 дыни в корзину
                    self.cart.add(melon, quantity=2)
                    promo_discount = Decimal(0)

                # 5 товаров, сумма меньше 1000
                elif i == 3:
                    # добавляем товары в корзину
                    self.cart.remove(melon)
                    self.cart.add(melon)
                    banana = offers[0]
                    self.cart.add(banana)
                    promo_discount = Decimal(0)

                # 5 товаров, сумма меньше 1000
                elif i == 4:
                    # добавляем товары в корзину
                    self.cart.add(melon, quantity=2)
                    promo_discount = self.cart.get_total_price() * promo.discount / 100

                # вычисляем скидку и сумму к оплате
                discount = self.cart.total_discount()
                due = self.cart.due()
                for_due = self.cart.get_total_price() - discount
                self.assertEqual(discount, promo_discount, promo_discount)
                self.assertEqual(due, for_due)


def create_category():
    """Создаются категории"""
    Category.objects.create(name='fruits', active=True)


def create_sellers():
    """Создает продавца"""
    user_1 = get_user_model().objects.create_user(password='test1234',
                                                  email='test1@test.ru',
                                                  phone="9787470001")
    Seller.objects.create(user=user_1, name='Shop1', description='test1',
                          address='test', number=1234567890)


def create_products():
    """Создает товары."""
    category_1 = Category.objects.get(name="fruits")

    products = [Product(name='banana',
                        description='description',
                        category=category_1),
                Product(name='apple',
                        description='description',
                        category=category_1),
                Product(name='orange',
                        description='description',
                        category=category_1),
                Product(name='pear',
                        description='description',
                        category=category_1),
                Product(name='melon',
                        description='description',
                        category=category_1),
                ]

    Product.objects.bulk_create(products)


def create_offers():
    """Создает предложения."""
    seller = Seller.objects.first()

    apple = Product.objects.get(name='apple')
    pear = Product.objects.get(name='pear')
    banana = Product.objects.get(name='banana')
    melon = Product.objects.get(name='melon')
    orange = Product.objects.get(name='orange')

    offers = [Offer(product=apple,
                    seller=seller,
                    price=50),
              Offer(product=pear,
                    seller=seller,
                    price=100),
              Offer(product=banana,
                    seller=seller,
                    price=120),
              Offer(product=melon,
                    seller=seller,
                    price=300),
              Offer(product=orange,
                    seller=seller,
                    price=80),
              ]

    Offer.objects.bulk_create(offers)


def promo_activate(name: str) -> Optional[Promo]:
    """
    Активирует акцию с именем name.
    :param name: Имя акции.
    :return:
    """
    try:
        promo = Promo.objects.get(name=name)
        promo.is_active = True
        promo.save()
        return promo
    except ObjectDoesNotExist:
        return None


def create_promotions():
    """Создает акции."""
    promo_type_1 = PromoType.objects.create(name='promo type 1', code=1)
    promo_type_3 = PromoType.objects.create(name='promo type 3', code=3)
    promo_type_4 = PromoType.objects.create(name='promo type 4', code=4)
    promo_type_5 = PromoType.objects.create(name='promo type 5', code=5)

    # акция на товар категорию товара code=1
    promo = Promo.objects.create(name='product discount',
                                 promo_type=promo_type_1,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=False,
                                 discount=5)

    promo2product = Promo2Product.objects.create(promo=promo)
    products = Product.objects.filter(name='apple')
    for product in products:
        promo2product.product.add(product)

    # акция на товар категорию товара code=1
    promo = Promo.objects.create(name='product fix discount',
                                 promo_type=promo_type_1,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=False,
                                 fix_discount=10)

    promo2product = Promo2Product.objects.create(promo=promo)
    products = Product.objects.filter(name='apple')
    for product in products:
        promo2product.product.add(product)

    # акция N+1 code=3
    promo = Promo.objects.create(name='promo 1+1',
                                 promo_type=promo_type_3,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=False,
                                 quantity=1)

    promo2product = Promo2Product.objects.create(promo=promo)
    products = Product.objects.filter(name='melon')
    for product in products:
        promo2product.product.add(product)

    # акция N+1 code=3
    promo = Promo.objects.create(name='promo 2+1',
                                 promo_type=promo_type_3,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=False,
                                 quantity=2)

    promo2product = Promo2Product.objects.create(promo=promo)
    products = Product.objects.filter(name='melon')
    for product in products:
        promo2product.product.add(product)

    # акция на N единиц товара code=4
    promo = Promo.objects.create(name='amount discount',
                                 promo_type=promo_type_4,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=False,
                                 discount=10,
                                 quantity=10)

    promo2product = Promo2Product.objects.create(promo=promo)
    products = Product.objects.filter(name='apple')
    for product in products:
        promo2product.product.add(product)

    # акция на N единиц товара code=4
    promo = Promo.objects.create(name='amount fix discount',
                                 promo_type=promo_type_4,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=False,
                                 fix_discount=100,
                                 quantity=10)

    promo2product = Promo2Product.objects.create(promo=promo)
    products = Product.objects.filter(name='apple')
    for product in products:
        promo2product.product.add(product)

    # акция на всю корзину code=5
    Promo.objects.create(name='cart',
                         promo_type=promo_type_5,
                         description='description',
                         finished=timezone.now(),
                         is_active=False,
                         discount=15,
                         quantity=5,
                         amount=Decimal(1000))
