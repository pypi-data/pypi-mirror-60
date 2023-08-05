import os

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Тестирование приложений проекта"

    def add_arguments(self, parser):
        parser.add_argument(
            dest="apps", nargs="+", help="Список приложений для тестирования"
        )

    def handle(self, **options):
        app_label_list = options.get("apps", [])
        for app_label in app_label_list:
            app_dir = apps.get_app_config(app_label).path
            os.system(f"python3 manage.py test {app_dir}")
