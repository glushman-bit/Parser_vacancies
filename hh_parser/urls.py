from django.urls import path

from hh_parser import views

urlpatterns = [
    path("", views.index, name="index"),
    path("database/create/", views.create_database, name="create_database"),
    path("load/test-data/", views.load_test_data, name="load_test_data"),
    path("load/hh/", views.load_hh_data, name="load_hh_data"),
    path("reports/companies-count/", views.report_companies_count, name="report_companies_count"),
    path("reports/all-vacancies/", views.report_all_vacancies, name="report_all_vacancies"),
    path("reports/avg-salary/", views.report_avg_salary, name="report_avg_salary"),
    path("reports/higher-salary/", views.report_higher_salary, name="report_higher_salary"),
    path("reports/search/", views.report_search, name="report_search"),
]
