from django.urls import path

from hh_parser.api_views import (
    AllVacanciesView,
    ApiRootView,
    AvgSalaryView,
    CompaniesListView,
    CompaniesVacanciesCountView,
    DatabaseCreateView,
    HigherSalaryView,
    LoadHHDataView,
    LoadTestDataView,
    SearchVacanciesView,
    VacanciesListView,
)

urlpatterns = [
    path("", ApiRootView.as_view(), name="api_root"),
    path("companies/", CompaniesListView.as_view(), name="api_companies"),
    path("vacancies/", VacanciesListView.as_view(), name="api_vacancies"),
    path("reports/companies-count/", CompaniesVacanciesCountView.as_view(), name="api_companies_count"),
    path("reports/all-vacancies/", AllVacanciesView.as_view(), name="api_all_vacancies"),
    path("reports/avg-salary/", AvgSalaryView.as_view(), name="api_avg_salary"),
    path("reports/higher-salary/", HigherSalaryView.as_view(), name="api_higher_salary"),
    path("reports/search/", SearchVacanciesView.as_view(), name="api_search"),
    path("database/create/", DatabaseCreateView.as_view(), name="api_database_create"),
    path("load/test-data/", LoadTestDataView.as_view(), name="api_load_test_data"),
    path("load/hh/", LoadHHDataView.as_view(), name="api_load_hh"),
]
