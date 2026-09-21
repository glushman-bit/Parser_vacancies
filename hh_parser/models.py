from django.db import models


class Company(models.Model):
    """Компания-работодатель."""

    company_id = models.IntegerField(primary_key=True, verbose_name="ID компании")
    name = models.CharField(max_length=50, verbose_name="Название")
    website = models.TextField(verbose_name="Сайт")
    vacancies = models.IntegerField(verbose_name="Количество вакансий")

    class Meta:
        db_table = "companies"
        ordering = ["name"]
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

    def __str__(self) -> str:
        return self.name


class Vacancy(models.Model):
    """Вакансия компании."""

    vacancy_id = models.IntegerField(primary_key=True, verbose_name="ID вакансии")
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        db_column="company_id",
        related_name="company_vacancies",
        verbose_name="Компания",
    )
    name = models.CharField(max_length=100, verbose_name="Название")
    published_at = models.DateField(null=True, blank=True, verbose_name="Дата публикации")
    salary_from = models.IntegerField(null=True, blank=True, verbose_name="Зарплата (от)")
    area = models.CharField(max_length=50, verbose_name="Регион")
    type = models.CharField(max_length=50, verbose_name="Тип занятости")
    website = models.TextField(verbose_name="Ссылка на вакансию")

    class Meta:
        db_table = "vacancies"
        ordering = ["-published_at"]
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

    def __str__(self) -> str:
        return self.name
