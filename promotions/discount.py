from decimal import Decimal
from django.db.models import Q, QuerySet

from promotions.models import Promo


def promos_for_product(product_id: int) -> QuerySet:
    """
    Возвращает список акций, в которых участвует товар.
    :param product_id: id товара
    :return:
    """
    promo_list = Promo.objects.filter(is_active=True).\
        filter(Q(promo2products__product=product_id) | Q(promo_type__code=5))

    return promo_list


def is_full_cart_discount(qty: int, total_price: Decimal, promo: Promo) -> bool:
    """
    Проверяет, может ли быть применена к товарам в корзине,
    скидка на всю корзину.
    :param qty: Количество наименований товаров в корзине.
    :param total_price: Общая стоимость корзины.
    :param promo: Информация об акции.
    :return:
    """
    if promo.amount == 0 and promo.quantity == 0:
        return False

    # необходимо купить N наименований товара на заданную сумму
    if promo.amount != 0 and promo.quantity != 0:
        if qty >= promo.quantity and total_price >= promo.amount:
            return True
    # необходимо купить товаров на заданную сумму
    elif promo.amount != 0:
        if total_price >= promo.amount:
            return True
    # необходимо купить N наименований товара не зависимо от суммы
    elif promo.quantity != 0:
        if qty >= promo.quantity:
            return True

    return False
