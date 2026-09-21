from django.db.models import Avg, F

from hh_parser.models import Company, Vacancy


class DBManager:
    """Класс для аналитических запросов к базе данных."""

    @staticmethod
    def get_companies_and_vacancies_count():
        """Список компаний и количество вакансий у каждой компании."""
        return list(Company.objects.order_by("-vacancies").values("name", "vacancies"))

    @staticmethod
    def get_all_vacancies():
        """Все вакансии (компания, вакансия, зарплата, ссылка)."""
        return [
            {
                "company": row["company__name"],
                "name": row["name"],
                "salary_from": row["salary_from"],
                "website": row["website"],
            }
            for row in Vacancy.objects.filter(salary_from__isnull=False)
            .order_by("company__name")
            .values("company__name", "name", "salary_from", "website")
        ]

    @staticmethod
    def get_avg_salary():
        """Средняя зарплата по компаниям."""
        rows = (
            Company.objects.annotate(
                avg_salary=Avg("company_vacancies__salary_from")
            )
            .order_by(F("avg_salary").desc(nulls_last=True))
            .values("name", "avg_salary")
        )
        return [
            {
                "name": row["name"],
                "avg_salary": round(row["avg_salary"]
                ) if row["avg_salary"] is not None else None
            }
            for row in rows
        ]

    @staticmethod
    def get_vacancies_with_higher_salary():
        """Вакансии с зарплатой не ниже средней по всем вакансиям."""
        avg_salary = Vacancy.objects.filter(
            salary_from__isnull=False
        ).aggregate(Avg("salary_from"))[
            "salary_from__avg"
        ]

        if avg_salary is None:
            return []

        return [
            {
                "company": row["company__name"],
                "name": row["name"],
                "salary_from": row["salary_from"]
            }
            for row in Vacancy.objects.filter(
                salary_from__gte=avg_salary
            ).values(
                "company__name",
                "name",
                "salary_from"
            )
        ]

    @staticmethod
    def get_vacancies_with_keyword(keyword: str):
        """Вакансии по ключевому слову в названии (без учёта регистра)."""
        return [
            {"company": row["company__name"],
             "name": row["name"],
             "salary_from": row["salary_from"]
             }
            for row in Vacancy.objects.filter(
                name__icontains=keyword
            ).values(
                "company__name",
                "name",
                "salary_from"
            )
        ]
