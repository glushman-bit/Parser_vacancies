from json import JSONDecodeError

import psycopg
from django.db import transaction

from hh_parser.models import Company, Vacancy
from hh_parser.services.api_hh import APIhh
from hh_parser.utils.config import Config
from hh_parser.utils.read_from_file import (
    path_file, read_companies_from_file, read_test_data, test_data_file)

REQUIRED_COMPANY_FIELDS = {
    "company_id",
    "name",
    "website",
    "vacancies",
}

REQUIRED_VACANCY_FIELDS = {
    "company_id",
    "vacancy_id",
    "name",
    "published_at",
    "salary_from",
    "area",
    "type",
    "website",
}


class TestDataError(Exception):
    """Ошибка загрузки тестовых данных."""


class DBWorker:
    """Класс создания базы данных и заполнения её данными."""

    def __init__(self, params: dict | None = None) -> None:
        self.params = params or Config.DB_PARAMS

    def create_database(self, database_name: str | None = None) -> str:
        """Создание базы данных, если она ещё не существует.

        Таблицы создаются механизмом миграций Django (python manage.py migrate).
        """
        database_name = database_name or Config.DATABASE_NAME
        conn = psycopg.connect(**self.params)
        conn.autocommit = True

        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
            database_exists = cur.fetchone() is not None

            if not database_exists:
                cur.execute(f'CREATE DATABASE "{database_name}"')
                message = f"База данных '{database_name}' создана."

            else:
                message = f"База данных '{database_name}' уже существует."

        conn.close()
        return message

    def save_to_db(self, employer_name) -> dict:
        """Заполнение базы данных данными с hh.ru."""
        api = APIhh()
        employers = api.get_employers(employer_name)

        companies_added = 0
        vacancies_added = 0

        with transaction.atomic():
            for company in employers:
                company_obj, _ = Company.objects.update_or_create(
                    company_id=company["id"],
                    defaults={
                        "name": company["name"],
                        "website": company["url"],
                        "vacancies": company["open_vacancies"],
                    },
                )
                companies_added += 1

                vacancies = api.get_vacancies(employer_id=company["id"])

                for vacancy in vacancies:
                    salary_from = vacancy["salary"]["from"] if vacancy["salary"] else None
                    published_at = vacancy["published_at"][:10] if vacancy["published_at"] else None

                    _, created = Vacancy.objects.get_or_create(
                        vacancy_id=vacancy["id"],
                        defaults={
                            "company": company_obj,
                            "name": vacancy["name"],
                            "published_at": published_at,
                            "salary_from": salary_from,
                            "area": vacancy["area"]["name"],
                            "type": vacancy["type"]["name"],
                            "website": vacancy["apply_alternate_url"],
                        },
                    )
                    if created:
                        vacancies_added += 1

        return {
            "companies": companies_added,
            "vacancies": vacancies_added,
            "message": (
                f"Данные с hh.ru успешно сохранены: "
                f"компаний — {companies_added}, вакансий — {vacancies_added}."
            ),
        }

    def validate_test_data(self, test_data: dict) -> None:
        """Проверка структуры тестовых данных."""
        if "companies" not in test_data:
            raise TestDataError("В тестовых данных отсутствует раздел 'companies'.")

        if "vacancies" not in test_data:
            raise TestDataError("В тестовых данных отсутствует раздел 'vacancies'.")

        for index, company in enumerate(test_data["companies"], start=1):
            missing_fields = REQUIRED_COMPANY_FIELDS - company.keys()

            if missing_fields:
                fields = ", ".join(sorted(missing_fields))
                raise TestDataError(f"Компания №{index}: отсутствуют поля: {fields}.")

        for index, vacancy in enumerate(test_data["vacancies"], start=1):
            missing_fields = REQUIRED_VACANCY_FIELDS - vacancy.keys()

            if missing_fields:
                fields = ", ".join(sorted(missing_fields))
                raise TestDataError(f"Вакансия №{index}: отсутствуют поля: {fields}.")

    def save_test_data(self) -> dict:
        """Очистка таблиц и заполнение базы тестовыми данными."""
        try:
            test_data = read_test_data(test_data_file)
            self.validate_test_data(test_data)

        except FileNotFoundError as e:
            raise TestDataError(f"Файл тестовых данных не найден: {test_data_file}") from e

        except JSONDecodeError as e:
            raise TestDataError(f"Ошибка формата JSON: строка {e.lineno}, столбец {e.colno}") from e

        try:
            with transaction.atomic():
                Vacancy.objects.all().delete()
                Company.objects.all().delete()

                Company.objects.bulk_create(
                    Company(
                        company_id=company["company_id"],
                        name=company["name"],
                        website=company["website"],
                        vacancies=company["vacancies"],
                    )
                    for company in test_data["companies"]
                )

                vacancies = []
                for company in test_data["companies"]:
                    company_obj = Company.objects.get(company_id=company["company_id"])
                    for vacancy in test_data["vacancies"]:
                        if vacancy["company_id"] != company["company_id"]:
                            continue
                        vacancies.append(
                            Vacancy(
                                vacancy_id=vacancy["vacancy_id"],
                                company=company_obj,
                                name=vacancy["name"],
                                published_at=vacancy["published_at"],
                                salary_from=vacancy["salary_from"],
                                area=vacancy["area"],
                                type=vacancy["type"],
                                website=vacancy["website"],
                            )
                        )
                Vacancy.objects.bulk_create(vacancies)

        except Exception:
            raise

        return {
            "companies": len(test_data["companies"]),
            "vacancies": len(test_data["vacancies"]),
            "message": (
                f"Тестовые данные успешно сохранены: "
                f"компаний — {len(test_data['companies'])}, вакансий — {len(test_data['vacancies'])}."
            ),
        }

    @staticmethod
    def load_companies_from_file() -> list[str]:
        """Чтение списка компаний из файла для загрузки с hh.ru."""
        return read_companies_from_file(path_file)
