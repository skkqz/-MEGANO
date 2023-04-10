from django import template
from django.http import HttpRequest

register = template.Library()


@register.simple_tag
def add_query_params(request: HttpRequest, **kwargs) -> str:
    """
    Добавляет или обновляет query часть URI
    :param request: объект HttpRequest
    :param kwargs: набор ключевых аргументов param1=val1
    :return: query часть URI

    Usage: {% add_query_params request param1=val1 param2=val2 ... %}
    """
    new_query = request.GET.copy()
    for key, value in kwargs.items():
        new_query[key] = value

    return new_query.urlencode()
