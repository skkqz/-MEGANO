## Генерация структуры моделей приложения

Автоматическая генерация файла, описывающего структуру моделей, выполняется с помощью расширения django-extensions,
дополняющего и расширяющего функционал скрипта `manage.py` командой `graph_models`. 
Представление моделей проекта в виде 
графов осуществляется с помощью графического пакета Graphviz.

### Порядок установки
1. Установите расширение `django-extensions`

        pip install django-extensions

2. Укажите расширение в `settings.py` в списке `INSTALLED_APPS`

        INSTALLED_APPS = [
            ....
            'django_extensions',
        ]

3. Установите утилиту `graphviz` в виртуальном окружении проекта

        sudo apt install graphviz graphviz-dev

4. Установите пакет `pygraphviz`

        pip install pygraphviz

5. Создайте dot-файл

        python manage.py graph_models -a > documents/models.dot

6. Создайте png-файл с визуализацией структуры моделей проекта

        python manage.py graph_models -a -g -o documents/models.png
