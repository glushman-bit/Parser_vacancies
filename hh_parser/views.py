from django.shortcuts import render

from hh_parser.services.api_hh import HHApiError
from hh_parser.services.db_manager import DBManager
from hh_parser.services.db_worker import DBWorker, TestDataError


def index(request):
    """Главное меню взаимодействия с пользователем."""
    return render(request, "hh_parser/index.html")


def create_database(request):
    """1 - Создать базу данных."""
    message = None
    error = None

    if request.method == "POST":
        try:
            db = DBWorker()
            message = db.create_database()

        except Exception as e:
            error = str(e)

    return _render_action(request, "Создание базы данных", message, error)


def load_test_data(request):
    """2 - Загрузить тестовые данные."""
    message = None
    error = None

    if request.method == "POST":
        db = DBWorker()

        try:
            result = db.save_test_data()
            message = result["message"]

        except TestDataError as e:
            error = str(e)

    return _render_action(request, "Загрузка тестовых данных", message, error)


def load_hh_data(request):
    """3 - Загрузить данные с HH.ru."""
    message = None
    error = None

    if request.method == "POST":
        db = DBWorker()

        try:
            companies = db.load_companies_from_file()
            result = db.save_to_db(companies)
            message = result["message"]

        except (HHApiError, TestDataError, Exception) as e:
            error = str(e)

    companies = DBWorker.load_companies_from_file()
    return render(
        request,
        "hh_parser/load_hh.html",
        {"title": "Загрузка данных с HH.ru", "message": message, "error": error, "companies": companies},
    )


def report_companies_count(request):
    """Отчёт: компании и количество вакансий."""
    columns = [
        {"key": "name", "label": "Компания"},
        {"key": "vacancies", "label": "Количество вакансий"}
    ]
    rows = DBManager.get_companies_and_vacancies_count()
    return _render_report(request, "Компании и количество вакансий", columns, rows)


def report_all_vacancies(request):
    """Отчёт: все вакансии."""
    columns = [
        {"key": "company", "label": "Компания"},
        {"key": "name", "label": "Вакансия"},
        {"key": "salary_from", "label": "Зарплата, руб."},
        {"key": "website", "label": "Интернет сайт"},
    ]
    return _render_report(request, "Все вакансии", columns, DBManager.get_all_vacancies())


def report_avg_salary(request):
    """Отчёт: средняя зарплата по компаниям."""
    columns = [{"key": "name", "label": "Компания"}, {"key": "avg_salary", "label": "Средняя зарплата, руб."}]
    rows = DBManager.get_avg_salary()
    return _render_report(request, "Средняя зарплата по компаниям", columns, rows)


def report_higher_salary(request):
    """Отчёт: вакансии с зарплатой выше средней."""
    columns = [
        {"key": "company", "label": "Компания"},
        {"key": "name", "label": "Вакансия"},
        {"key": "salary_from", "label": "Зарплата, руб."},
    ]
    rows = DBManager.get_vacancies_with_higher_salary()
    return _render_report(request, "Вакансии с зарплатой выше средней", columns, rows)


def report_search(request):
    """Отчёт: поиск вакансий по ключевому слову."""
    keyword = request.GET.get("keyword", "")
    rows = DBManager.get_vacancies_with_keyword(keyword) if keyword else []
    columns = [
        {"key": "company", "label": "Компания"},
        {"key": "name", "label": "Вакансия"},
        {"key": "salary_from", "label": "Зарплата, руб."},
    ]
    return render(
        request,
        "hh_parser/search.html",
        {"title": "Поиск вакансий по ключевому слову", "columns": columns, "rows": rows, "keyword": keyword},
    )


def _render_action(request, title, message, error):
    """Рендер страницы выполнения действия с сообщением или ошибкой."""
    return render(
        request,
        "hh_parser/action_result.html",
        {"title": title, "message": message, "error": error},
    )


def _render_report(request, title, columns, rows):
    """Рендер страницы отчёта с таблицей."""
    return render(request, "hh_parser/report.html", {"title": title, "columns": columns, "rows": rows})
