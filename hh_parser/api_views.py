from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from hh_parser.models import Company, Vacancy
from hh_parser.serializers import (
    AvgSalarySerializer,
    CompanySerializer,
    CompanyVacanciesCountSerializer,
    DatabaseCreateSerializer,
    LoadResultSerializer,
    ReportRowSerializer,
    VacancySerializer,
)
from hh_parser.services.api_hh import HHApiError
from hh_parser.services.db_manager import DBManager
from hh_parser.services.db_worker import DBWorker, TestDataError


class ApiRootView(APIView):
    """GET /api/ — список доступных эндпоинтов."""

    def get(self, request):
        endpoints = [
            ("companies", "/api/companies/", "Список компаний"),
            ("vacancies", "/api/vacancies/", "Список вакансий"),
            ("search", "/api/vacancies/?keyword=<слово>", "Поиск вакансий по ключевому слову"),
            ("companies-count", "/api/reports/companies-count/", "Компании и количество вакансий"),
            ("all-vacancies", "/api/reports/all-vacancies/", "Все вакансии"),
            ("avg-salary", "/api/reports/avg-salary/", "Средняя зарплата по компаниям"),
            ("higher-salary", "/api/reports/higher-salary/", "Вакансии с зарплатой выше средней"),
            ("search-report", "/api/reports/search/?keyword=<слово>", "Поиск вакансий по ключевому слову"),
            ("create-database", "/api/database/create/", "Создание базы данных (POST)"),
            ("load-test-data", "/api/load/test-data/", "Загрузка тестовых данных (POST)"),
            ("load-hh", "/api/load/hh/", "Загрузка данных с hh.ru (POST)"),
        ]
        return Response({name: {"url": url, "description": description} for name, url, description in endpoints})


class CompaniesListView(APIView):
    """GET /api/companies/ — список компаний."""

    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)


class VacanciesListView(APIView):
    """GET /api/vacancies/ — список вакансий, GET /api/vacancies/?keyword= — поиск по ключевому слову."""

    def get(self, request):
        keyword = request.query_params.get("keyword", "").strip()

        if keyword:
            rows = DBManager.get_vacancies_with_keyword(keyword)
            serializer = ReportRowSerializer(rows, many=True)
            return Response(serializer.data)

        vacancies = Vacancy.objects.select_related("company").all()
        serializer = VacancySerializer(vacancies, many=True)
        return Response(serializer.data)


class CompaniesVacanciesCountView(APIView):
    """GET /api/reports/companies-count/ — компании и количество вакансий."""

    def get(self, request):
        rows = DBManager.get_companies_and_vacancies_count()
        serializer = CompanyVacanciesCountSerializer(rows, many=True)
        return Response(serializer.data)


class AllVacanciesView(APIView):
    """GET /api/reports/all-vacancies/ — все вакансии."""

    def get(self, request):
        rows = DBManager.get_all_vacancies()
        serializer = ReportRowSerializer(rows, many=True)
        return Response(serializer.data)


class AvgSalaryView(APIView):
    """GET /api/reports/avg-salary/ — средняя зарплата по компаниям."""

    def get(self, request):
        rows = DBManager.get_avg_salary()
        serializer = AvgSalarySerializer(rows, many=True)
        return Response(serializer.data)


class HigherSalaryView(APIView):
    """GET /api/reports/higher-salary/ — вакансии с зарплатой выше средней."""

    def get(self, request):
        rows = DBManager.get_vacancies_with_higher_salary()
        serializer = ReportRowSerializer(rows, many=True)
        return Response(serializer.data)


class SearchVacanciesView(APIView):
    """GET /api/reports/search/?keyword= — поиск вакансий по ключевому слову."""

    def get(self, request):
        keyword = request.query_params.get("keyword", "").strip()

        if not keyword:
            return Response({"keyword": "Поле 'keyword' обязательно для поиска."}, status=status.HTTP_400_BAD_REQUEST)

        rows = DBManager.get_vacancies_with_keyword(keyword)
        serializer = ReportRowSerializer(rows, many=True)
        return Response(serializer.data)


class DatabaseCreateView(APIView):
    """POST /api/database/create/ — создание базы данных."""

    def post(self, request):
        db = DBWorker()
        message = db.create_database()
        serializer = DatabaseCreateSerializer({"message": message})
        return Response(serializer.data)


class LoadTestDataView(APIView):
    """POST /api/load/test-data/ — загрузка тестовых данных."""

    def post(self, request):
        db = DBWorker()

        try:
            result = db.save_test_data()

        except (TestDataError, Exception) as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LoadResultSerializer(result)
        return Response(serializer.data)


class LoadHHDataView(APIView):
    """POST /api/load/hh/ — загрузка данных с hh.ru."""

    def post(self, request):
        db = DBWorker()

        try:
            companies = db.load_companies_from_file()
            result = db.save_to_db(companies)

        except (HHApiError, Exception) as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LoadResultSerializer(result)
        return Response(serializer.data)
