"""Загрузка тестовых данных из data/test_data.json.

Аналог пункта меню «2 - Загрузить тестовые данные»: python manage.py load_test_data
"""

from django.core.management.base import BaseCommand

from hh_parser.services.db_worker import DBWorker, TestDataError


class Command(BaseCommand):
    help = "Очистка таблиц и загрузка тестовых данных."

    def handle(self, *args, **options):
        db = DBWorker()

        try:
            result = db.save_test_data()
            self.stdout.write(self.style.SUCCESS(result["message"]))

        except TestDataError as e:
            self.stderr.write(self.style.ERROR(f"Ошибка загрузки тестовых данных: {e}"))
