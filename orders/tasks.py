import random
import time
from celery import shared_task
from django.shortcuts import get_object_or_404
from .models import Order


@shared_task
def payment(pk):
    time.sleep(15)
    card = get_object_or_404(Order, pk=pk)
    card_number = card.card_number
    errors_list = [
        'Ошибка сервера',
        'Банк отклонил платеж',
        'Неправильный номер счета',
        'Недостаточно средств',
        'Счет заблокирован'
    ]

    if int(card_number) % 2 or str(card_number)[-1] == '0':
        status = random.choice(errors_list)
        card.status_payment = status
        card.payment_code = 1
        card.save()
        return
    card.status_payment = 'Оплата прошла успешно'
    card.payment_code = 1
    card.save()
