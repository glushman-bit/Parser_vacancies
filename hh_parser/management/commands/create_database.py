"""Создание базы данных 'headhunter' и применение миграций.

Аналог пункта меню «1 - Создать базу данных»: python manage.py create_database
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand

from hh_parser.services.db_worker import DBWorker


class Command(BaseCommand):
    help = "Создание базы данных (таблицы создаются миграциями)."

    def handle(self, *args, **options):
        db = DBWorker()
        message = db.create_database()
        self.stdout.write(self.style.SUCCESS(message))
        call_command("migrate", verbosity=1)
