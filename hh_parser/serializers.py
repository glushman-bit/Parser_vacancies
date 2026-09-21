from rest_framework import serializers

from hh_parser.models import Company, Vacancy


class CompanySerializer(serializers.ModelSerializer):
    """Сериализатор компании."""

    class Meta:
        model = Company
        fields = ("company_id", "name", "website", "vacancies")


class VacancySerializer(serializers.ModelSerializer):
    """Сериализатор вакансии."""

    company = CompanySerializer(read_only=True)

    class Meta:
        model = Vacancy
        fields = ("vacancy_id", "company", "name", "published_at", "salary_from", "area", "type", "website")


class CompanyVacanciesCountSerializer(serializers.Serializer):
    """Компания и количество вакансий."""

    name = serializers.CharField()
    vacancies = serializers.IntegerField()


class ReportRowSerializer(serializers.Serializer):
    """Строка аналитического отчёта о вакансии."""

    company = serializers.CharField()
    name = serializers.CharField()
    salary_from = serializers.IntegerField(allow_null=True)
    website = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AvgSalarySerializer(serializers.Serializer):
    """Средняя зарплата по компании."""

    name = serializers.CharField()
    avg_salary = serializers.IntegerField(allow_null=True)


class LoadResultSerializer(serializers.Serializer):
    """Результат загрузки данных."""

    message = serializers.CharField()
    companies = serializers.IntegerField(required=False)
    vacancies = serializers.IntegerField(required=False)


class DatabaseCreateSerializer(serializers.Serializer):
    """Результат создания базы данных."""

    message = serializers.CharField()
