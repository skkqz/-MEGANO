## Генерация структуры urls приложения

Автоматическая генерация файла, описывающего структуру urls, выполняется с помощью расширения django-extensions,
дополняющего и расширяющего функционал скрипта `manage.py` командой `show_urls`. 
Представление urls проекта в виде 
Списка всех адресов и используемых представлений.

### Порядок установки
1. Установите расширение `django-extensions`

        pip install django-extensions

2. Укажите расширение в `settings.py` в списке `INSTALLED_APPS`

        INSTALLED_APPS = [
            ....
            'django_extensions',
        ]

3. Создайте txt-файл со списком всех urls проекта 

        python manage.py show_urls > urls.txt


