from django.contrib import admin

from hh_parser.models import Company, Vacancy


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("company_id", "name", "website", "vacancies")
    search_fields = ("name",)


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("vacancy_id", "name", "company", "salary_from", "area", "type", "published_at")
    list_filter = ("area", "type", "company")
    search_fields = ("name", "company__name")
