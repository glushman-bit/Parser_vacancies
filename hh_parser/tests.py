from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from hh_parser.models import Company, Vacancy
from hh_parser.services.db_manager import DBManager
from hh_parser.services.db_worker import DBWorker, TestDataError

TEST_DATA = {
    "companies": [
        {"company_id": 1001, "name": "Яндекс", "website": "https://yandex.ru", "vacancies": 2},
        {"company_id": 1002, "name": "VK", "website": "https://vk.company", "vacancies": 1},
    ],
    "vacancies": [
        {
            "company_id": 1001,
            "vacancy_id": 20001,
            "name": "Python Developer",
            "published_at": "2026-08-20",
            "salary_from": 180000,
            "area": "Москва",
            "type": "Полная занятость",
            "website": "https://hh.ru/vacancy/20001",
        },
        {
            "company_id": 1001,
            "vacancy_id": 20002,
            "name": "QA Engineer",
            "published_at": "2026-08-10",
            "salary_from": None,
            "area": "Москва",
            "type": "Полная занятость",
            "website": "https://hh.ru/vacancy/20002",
        },
        {
            "company_id": 1002,
            "vacancy_id": 20003,
            "name": "Java Developer",
            "published_at": "2026-08-19",
            "salary_from": 200000,
            "area": "Москва",
            "type": "Полная занятость",
            "website": "https://hh.ru/vacancy/20003",
        },
    ],
}


class DBWorkerTest(TestCase):
    def test_validate_test_data_ok(self):
        DBWorker().validate_test_data(TEST_DATA)

    def test_validate_test_data_missing_field(self):
        data = {"companies": TEST_DATA["companies"][:], "vacancies": TEST_DATA["vacancies"][:]}
        data["vacancies"][0] = {k: v for k, v in data["vacancies"][0].items() if k != "area"}

        with self.assertRaises(TestDataError) as ctx:
            DBWorker().validate_test_data(data)

        self.assertIn("Вакансия №1", str(ctx.exception))
        self.assertIn("area", str(ctx.exception))

    @patch("hh_parser.services.db_worker.read_test_data", return_value=TEST_DATA)
    def test_save_test_data(self, _):
        result = DBWorker().save_test_data()
        self.assertEqual(result["companies"], 2)
        self.assertEqual(result["vacancies"], 3)
        self.assertEqual(Company.objects.count(), 2)
        self.assertEqual(Vacancy.objects.count(), 3)


def _load_fixture() -> None:
    """Загрузка тестовой фикстуры напрямую через ORM."""
    for company in TEST_DATA["companies"]:
        Company.objects.create(
            company_id=company["company_id"],
            name=company["name"],
            website=company["website"],
            vacancies=company["vacancies"],
        )

    for vacancy in TEST_DATA["vacancies"]:
        company = Company.objects.get(company_id=vacancy["company_id"])
        Vacancy.objects.create(
            vacancy_id=vacancy["vacancy_id"],
            company=company,
            name=vacancy["name"],
            published_at=vacancy["published_at"],
            salary_from=vacancy["salary_from"],
            area=vacancy["area"],
            type=vacancy["type"],
            website=vacancy["website"],
        )


class DBManagerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        _load_fixture()

    def test_companies_and_vacancies_count(self):
        rows = DBManager.get_companies_and_vacancies_count()
        self.assertEqual(len(rows), 2)

    def test_all_vacancies_excludes_null_salary(self):
        rows = DBManager.get_all_vacancies()
        names = [row["name"] for row in rows]
        self.assertIn("Python Developer", names)
        self.assertNotIn("QA Engineer", names)

    def test_avg_salary(self):
        rows = DBManager.get_avg_salary()
        by_name = {row["name"]: row["avg_salary"] for row in rows}
        self.assertEqual(by_name["Яндекс"], 180000)
        self.assertEqual(by_name["VK"], 200000)

    def test_vacancies_with_higher_salary(self):
        rows = DBManager.get_vacancies_with_higher_salary()
        self.assertEqual([row["name"] for row in rows], ["Java Developer"])

    def test_vacancies_with_keyword(self):
        rows = DBManager.get_vacancies_with_keyword("python")
        self.assertEqual([row["name"] for row in rows], ["Python Developer"])


class ApiTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        _load_fixture()

    def test_companies_list(self):
        resp = self.client.get("/api/companies/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 2)

    def test_vacancies_search(self):
        resp = self.client.get("/api/vacancies/?keyword=python")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_report_higher_salary(self):
        resp = self.client.get("/api/reports/higher-salary/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_search_requires_keyword(self):
        resp = self.client.get("/api/reports/search/")
        self.assertEqual(resp.status_code, 400)


class TemplateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        _load_fixture()

    def test_index_page(self):
        resp = self.client.get(reverse("index"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "менеджер по работе с базой данных")

    def test_report_avg_salary_page(self):
        resp = self.client.get(reverse("report_avg_salary"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "180 000")
