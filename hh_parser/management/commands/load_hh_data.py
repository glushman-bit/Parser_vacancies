"""Загрузка данных с hh.ru по списку компаний из data/companies.txt.

Аналог пункта меню «3 - Загрузить данные с HH.ru»: python manage.py load_hh_data
"""

from django.core.management.base import BaseCommand

from hh_parser.services.api_hh import HHApiError
from hh_parser.services.db_worker import DBWorker


class Command(BaseCommand):
    help = "Загрузка данных о компаниях и вакансиях с hh.ru."

    def handle(self, *args, **options):
        db = DBWorker()

        try:
            companies = db.load_companies_from_file()
            result = db.save_to_db(companies)
            self.stdout.write(self.style.SUCCESS(result["message"]))

        except HHApiError as e:
            self.stderr.write(self.style.ERROR(f"Ошибка загрузки данных с HH.ru: {e}"))
