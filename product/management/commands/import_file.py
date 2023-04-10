import os
from django.core.management.base import BaseCommand
from product.import_file_test import parsing_json_file


class Command(BaseCommand):

    help = 'Команда для добавление файла'

    def add_arguments(self, parser):
        parser.add_argument('name_file', type=str, help=u'Имя файла')

    def handle(self, *args, **kwargs):
        name = kwargs['name_file']
        path = os.path.abspath(os.path.join(f'media/import_files/queued_files/{name}'))

        if os.path.isfile(path):
            parsing_json_file(path)
        else:
            print(f'Файла {name} не существует в директории !')
