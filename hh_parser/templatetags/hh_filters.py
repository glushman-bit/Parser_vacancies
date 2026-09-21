from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    """Возвращает значение словаря по ключу."""
    return mapping.get(key)


@register.filter
def format_salary(salary):
    """Красиво форматирует зарплату."""
    if salary is None:
        return "Нет данных"
    return f"{salary:,}".replace(",", " ")
