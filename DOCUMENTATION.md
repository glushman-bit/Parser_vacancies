# Документация по методам и функциям проекта Parser Vacancies

Ниже приведены комментарии ко всем используемым в проекте методам и функциям, сгруппированные по модулям. Для каждого метода указаны назначение, сигнатура, параметры, возвращаемое значение и используемые внутри инструменты (Django ORM, DRF и стандартная библиотека).

---

## Структура документации

1. [Модели ORM — `hh_parser/models.py`](#1-модели-orm--hh_parsermodelspy)
2. [Сервис работы с API hh.ru — `hh_parser/services/api_hh.py`](#2-сервис-работы-с-api-hhru--hh_parserservicesapi_hhpy)
3. [Сервис создания БД и загрузки данных — `hh_parser/services/db_worker.py`](#3-сервис-создания-бд-и-загрузки-данных--hh_parserservicesdb_workerpy)
4. [Сервис аналитических запросов — `hh_parser/services/db_manager.py`](#4-сервис-аналитических-запросов--hh_parserservicesdb_managerpy)
5. [Конфигурация окружения — `hh_parser/utils/config.py`](#5-конфигурация-окружения--hh_parserutilsconfigpy)
6. [Чтение файлов — `hh_parser/utils/read_from_file.py`](#6-чтение-файлов--hh_parserutilsread_from_filepy)
7. [Сериализаторы DRF — `hh_parser/serializers.py`](#7-сериализаторы-drf--hh_parserserializerspy)
8. [REST API представления — `hh_parser/api_views.py`](#8-rest-api-представления--hh_parserapi_viewspy)
9. [Представления шаблонов — `hh_parser/views.py`](#9-представления-шаблонов--hh_parserviewspy)
10. [Теги шаблонов — `hh_parser/templatetags/hh_filters.py`](#10-теги-шаблонов--hh_parsertemplatetagshh_filterspy)
11. [Management-команды](#11-management-команды)
12. [Тесты — `hh_parser/tests.py`](#12-тесты--hh_parsertestspy)
13. [Параметры конфигурации Django — `config/settings.py`](#13-параметры-конфигурации-django--configsettingspy)

---

## 1. Модели ORM — `hh_parser/models.py`

Модуль определяет ORM-модели Django, соответствующие таблицам исходного проекта Proj_HH.

### Модель `Company`
```python
class Company(models.Model)
```
Компания-работодатель. Наследует `django.db.models.Model`.

| Поле | Тип | Описание |
| --- | --- | --- |
| `company_id` | `IntegerField(primary_key=True)` | ID компании, первичный ключ (совпадает с внешним ID hh.ru) |
| `name` | `CharField(max_length=50)` | Название компании |
| `website` | `TextField()` | Ссылка на сайт компании |
| `vacancies` | `IntegerField()` | Количество открытых вакансий |

`Meta`: `db_table = "companies"` — имя таблицы совпадает с исходной схемой Proj_HH.

- **`__str__(self) -> str`** — возвращает название компании (используется в админке и при отображении).

### Модель `Vacancy`
```python
class Vacancy(models.Model)
```
Вакансия компании.

| Поле | Тип | Описание |
| --- | --- | --- |
| `vacancy_id` | `IntegerField(primary_key=True)` | ID вакансии, первичный ключ |
| `company` | `ForeignKey(Company, on_delete=CASCADE, db_column="company_id", related_name="company_vacancies")` | Компания; физическая колонка `company_id` |
| `name` | `CharField(max_length=100)` | Название вакансии |
| `published_at` | `DateField(null=True, blank=True)` | Дата публикации |
| `salary_from` | `IntegerField(null=True, blank=True)` | Нижняя граница зарплаты |
| `area` | `CharField(max_length=50)` | Регион |
| `type` | `CharField(max_length=50)` | Тип занятости |
| `website` | `TextField()` | Ссылка на вакансию |

`Meta`: `db_table = "vacancies"`, `ordering = ["-published_at"]` — по умолчанию сортировка по дате публикации по убыванию.

- **`__str__(self) -> str`** — возвращает название вакансии.

Используемые методы Django ORM (через менеджер `objects`):
- `.objects.all()` — получить все записи;
- `.objects.order_by("-vacancies")` — сортировка по полю по убыванию;
- `.objects.annotate(...)` — агрегация с добавлением вычисляемого поля;
- `.objects.aggregate(...)` — вычисление агрегата по всему набору;
- `.objects.filter(...)`, `.values(...)`, `.select_related(...)` — см. раздел 4.

---

## 2. Сервис работы с API hh.ru — `hh_parser/services/api_hh.py`

### Исключение `HHApiError`
```python
class HHApiError(Exception)
```
Собственное исключение для ошибок при работе с API hh.ru. Продублировано из исходного проекта Proj_HH.

### Класс `APIhh`
```python
class APIhh
```
Аналог `src/APIhh.py` исходного проекта. Инкапсулирует HTTP-запросы к API hh.ru через библиотеку `requests`.

- **`__init__(self) -> None`**
  Задаёт `self.base_url = "https://api.hh.ru"` и `self.headers = {"User-Agent": "hh_api_db/1.0"}`. Заголовок `User-Agent` требуется политикой hh.ru.

- **`get_employers(self, employer_name: list[str])`**
  Получение данных работодателей.
  - *Параметры:* `employer_name` — список названий компаний.
  - *Логика:* для каждого названия выполняет GET к `/employers` с параметрами `{"text": name, "only_with_vacancies": True, "type": "company", "area": 113}` и берёт первый найденный элемент `items[0]`; между запросами пауза `time.sleep(0.2)`.
  - *Возвращает:* список словарей с данными работодателей.
  - *Исключения:* `HHApiError` — при `requests.RequestException`, при HTTP-статусе ≠ 200 и при пустом ответе.
  - Используемые функции и методы:
    - `requests.get(url, params=params, headers=self.headers)` — HTTP GET-запрос;
    - `requests.RequestException` — базовое исключение ошибок сети/HTTP `requests`;
    - `response.status_code` — код ответа;
    - `response.json()` — разбор JSON-ответа;
    - `.get("items")` — безопасное чтение ключа из словаря;
    - `time.sleep(0.2)` — задержка для соблюдения лимитов API;
    - `raise ... from e` — цепочка исключений (сохранение исходной ошибки).

- **`get_vacancies(self, employer_id: str)`**
  Получение вакансий конкретного работодателя.
  - *Параметры:* `employer_id` — ID работодателя.
  - *Логика:* GET к `/vacancies` с параметрами `{"employer_id": employer_id, "per_page": 30}`.
  - *Возвращает:* список словарей вакансий (ключ `items`, по умолчанию `[]`).
  - *Исключения:* `HHApiError` — при `requests.RequestException` и при HTTP-статусе ≠ 200.

---

## 3. Сервис создания БД и загрузки данных — `hh_parser/services/db_worker.py`

Модуль содержит константы обязательных полей, собственное исключение и класс `DBWorker` — аналог `src/DBWorker.py`.

### Константы
- `REQUIRED_COMPANY_FIELDS = {"company_id", "name", "website", "vacancies"}` — обязательные поля компании в тестовых данных.
- `REQUIRED_VACANCY_FIELDS = {"company_id", "vacancy_id", "name", "published_at", "salary_from", "area", "type", "website"}` — обязательные поля вакансии в тестовых данных.

### Исключение `TestDataError`
```python
class TestDataError(Exception)
```
Ошибка загрузки или валидации тестовых данных. Аналог одноимённого класса исходного проекта.

### Класс `DBWorker`
```python
class DBWorker
```
Создание базы данных и заполнение её данными (с hh.ru или тестовыми).

- **`__init__(self, params: dict | None = None) -> None`**
  Инициализация параметров подключения к PostgreSQL. Если `params` не передан, берутся `Config.DB_PARAMS` из `.env`.

- **`create_database(self, database_name: str | None = None) -> str`**
  Создание базы данных, если она ещё не существует.
  - *Логика:* через `psycopg2.connect(**self.params)` (без имени БД — подключение к серверу) проверяет наличие БД запросом `SELECT 1 FROM pg_database WHERE datname = %s` и выполняет `CREATE DATABASE`, если её нет. Транзакция включена через `conn.autocommit = True`. Таблицы создаются миграциями Django.
  - *Параметры:* `database_name` — имя создаваемой БД (по умолчанию `Config.DATABASE_NAME`).
  - *Возвращает:* строку-сообщение «База данных '...' создана.» или «... уже существует.».
  - Используемые методы и функции:
    - `psycopg2.connect(**params)` — подключение к PostgreSQL;
    - `conn.cursor()` — создание курсора;
    - `cur.execute(sql, params)` — выполнение SQL-запроса с параметрами (защита от SQL-инъекций);
    - `cur.fetchone()` — получение одной строки результата;
    - `conn.autocommit = True` — автокоммит (необходим для `CREATE DATABASE`);
    - `conn.close()` — закрытие соединения.

- **`save_to_db(self, employer_name) -> dict`**
  Заполнение базы данных данными с hh.ru.
  - *Логика:* создаёт `APIhh()`, получает работодателей по названиям, для каждого — вакансии. Компании записываются через `update_or_create`, вакансии — через `get_or_create` (аналог `INSERT ... ON CONFLICT DO NOTHING`). Вся запись обёрнута в `transaction.atomic()`.
  - *Параметры:* `employer_name` — список названий компаний (обычно из `data/companies.txt`).
  - *Возвращает:* словарь `{"companies": кол-во, "vacancies": кол-во, "message": str}`.
  - Используемые методы и функции Django ORM:
    - `Company.objects.update_or_create(company_id=..., defaults={...})` — создать, если нет, иначе обновить; возвращает `(объект, created)`; аналог SQL `INSERT ... ON CONFLICT (company_id) DO UPDATE`;
    - `Vacancy.objects.get_or_create(vacancy_id=..., defaults={...})` — создать, если нет; возвращает `(объект, created)`; аналог `INSERT ... ON CONFLICT (vacancy_id) DO NOTHING`;
    - `transaction.atomic()` — контекстный менеджер транзакции (коммит при успехе, откат при ошибке).
  - Обработка полей API:
    - `vacancy["salary"]["from"] if vacancy["salary"] else None` — зарплата может отсутствовать;
    - `vacancy["published_at"][:10]` — обрезка ISO-даты до `YYYY-MM-DD`;
    - `vacancy["apply_alternate_url"]` — ссылка на вакансию.

- **`validate_test_data(self, test_data: dict) -> None`**
  Проверка структуры тестовых данных JSON.
  - *Логика:* проверяет наличие разделов `companies` и `vacancies`; для каждой записи вычисляет `REQUIRED_..._FIELDS - dict.keys()` и при непустой разности выбрасывает `TestDataError` с номером записи и списком полей.
  - Используемые операции: разность множеств `set - dict_keys`, `", ".join(sorted(missing_fields))`.

- **`save_test_data(self) -> dict`**
  Очистка таблиц и загрузка тестовых данных из `data/test_data.json`.
  - *Логика:*
    1. `read_test_data(test_data_file)` читает JSON, затем `validate_test_data(...)`;
    2. при отсутствии файла — `TestDataError` из `FileNotFoundError`;
    3. при некорректном JSON — `TestDataError` из `JSONDecodeError` (с номером строки и колонки);
    4. в `transaction.atomic()` удаляет все вакансии и компании, затем записывает компании одним вызовом `bulk_create` и вакансии (связанные по `company_id`) вторым `bulk_create`.
  - *Возвращает:* словарь `{"companies": N, "vacancies": N, "message": str}`.
  - Используемые методы и функции Django ORM:
    - `Vacancy.objects.all().delete()` / `Company.objects.all().delete()` — очистка таблиц;
    - `Company.objects.bulk_create(iterable)` — массовая вставка за один SQL-запрос;
    - `Vacancy.objects.bulk_create(iterable)`; `Company.objects.get(company_id=...)` — получение объекта для связи FK.

- **`load_companies_from_file() -> list[str]`** *(staticmethod)*
  Чтение списка названий компаний из `data/companies.txt` для загрузки с hh.ru.
  - *Возвращает:* список строк.
  - Использует функцию `read_companies_from_file(path_file)` из утилит.

---

## 4. Сервис аналитических запросов — `hh_parser/services/db_manager.py`

### Класс `DBManager`
```python
class DBManager
```
Аналог `src/DBManager.py` оригинального проекта. Все методы — `staticmethod`, возвращают список словарей (готовых к сериализации в DRF).

- **`get_companies_and_vacancies_count()`**
  Список компаний и количество вакансий каждой.
  - SQL-эквивалент: `SELECT name, vacancies FROM companies ORDER BY vacancies DESC`.
  - Использует: `Company.objects.order_by("-vacancies").values("name", "vacancies")` — `.values()` возвращает словари вместо объектов.

- **`get_all_vacancies()`**
  Все вакансии с указанной зарплатой.
  - SQL-эквивалент: `... WHERE salary_from IS NOT NULL`.
  - Использует: `Vacancy.objects.filter(salary_from__isnull=False).order_by("company__name").values("company__name", ...)` — `filter()` с `__isnull=False`, соединение по FK через `company__name`.

- **`get_avg_salary()`**
  Средняя зарплата по компаниям.
  - SQL-эквивалент: `AVG(vac.salary_from)` с группировкой по компании и `ORDER BY avg DESC NULLS LAST`.
  - Использует:
    - `Company.objects.annotate(avg_salary=Avg("company_vacancies__salary_from"))` — `annotate()` + агрегат `Avg` через обратную связь (`related_name="company_vacancies"`);
    - `.order_by(F("avg_salary").desc(nulls_last=True))` — сортировка по вычисляемому полю `F()` с `NULLS LAST`;
    - `.values("name", "avg_salary")`;
    - `round(value)` — округление (аналог `ROUND()` в SQL); `None` не трогается.

- **`get_vacancies_with_higher_salary()`**
  Вакансии с зарплатой не ниже средней по всем вакансиям.
  - Логика: сначала `Vacancy.objects.filter(salary_from__isnull=False).aggregate(Avg("salary_from"))` — `aggregate()` возвращает одно число; затем `filter(salary_from__gte=avg_salary)` (`>=`).
  - Возвращает `[]`, если средняя зарплата `None` (нет данных).

- **`get_vacancies_with_keyword(keyword: str)`**
  Поиск вакансий по ключевому слову без учёта регистра.
  - Использует `filter(name__icontains=keyword)` — Django-лукап `icontains`, SQL-эквивалент `LOWER(vac.name) LIKE LOWER(%s)`.

Используемые функции/агрегаты `django.db.models`:
- `Avg("field")` — среднее значение;
- `F("field")` — ссылка на поле/выражение в SQL (используется для сортировки по аннотации с `nulls_last`).

---

## 5. Конфигурация окружения — `hh_parser/utils/config.py`

### Класс `Config`
```python
class Config
```
Параметры подключения к PostgreSQL, читаемые из `.env` при помощи `python-dotenv`.

- `load_dotenv()` — загрузка переменных окружения из файла `.env`.
- `DATABASE_NAME` — имя БД (по умолчанию `"headhunter"`).
- `POSTGRES_HOST` — хост (по умолчанию `"localhost"`).
- `POSTGRES_USER` — пользователь (по умолчанию `"postgres"`).
- `POSTGRES_PASSWORD` — пароль (по умолчанию `""`).
- `POSTGRES_PORT` — порт (по умолчанию `"5432"`).
- `DB_PARAMS` — словарь `{"host", "user", "password", "port"}` для `psycopg2.connect(**params)`.

Используемые функции:
- `os.getenv(name, default)` — чтение переменной окружения с значением по умолчанию;
- `dotenv.load_dotenv()` — загрузка `.env`.

---

## 6. Чтение файлов — `hh_parser/utils/read_from_file.py`

### Модульные константы
- `BASE_DIR = Path(__file__).resolve().parent.parent.parent` — корень проекта (три уровня вверх от `hh_parser/utils/`).
- `DATA_DIR = BASE_DIR / "data"` — каталог данных.
- `path_file = DATA_DIR / "companies.txt"` — файл списка компаний.
- `test_data_file = DATA_DIR / "test_data.json"` — файл тестовых данных.

### Функции
- **`read_companies_from_file(file_path)`**
  Чтение списка компаний из текстового файла.
  - *Логика:* построчно читает файл в кодировке `utf-8`, отбрасывает пустые строки и `strip()`-ит каждую (`[line.strip() for line in f if line.strip()]`).
  - *Возвращает:* список строк.

- **`read_test_data(file_path)`**
  Чтение тестовых данных из JSON-файла.
  - *Логика:* `json.load(f)` парсит JSON.
  - *Возвращает:* словарь.
  - Исключение `JSONDecodeError` обрабатывается в `DBWorker.save_test_data()`.

---

## 7. Сериализаторы DRF — `hh_parser/serializers.py`

Модуль определяет сериализаторы Django REST Framework.

| Класс | Наследует | Назначение | Поля |
| --- | --- | --- | --- |
| `CompanySerializer` | `serializers.ModelSerializer` | Сериализация модели `Company` | `company_id`, `name`, `website`, `vacancies` |
| `VacancySerializer` | `serializers.ModelSerializer` | Сериализация модели `Vacancy` | `vacancy_id`, `company` (вложенный `CompanySerializer`, `read_only`), `name`, `published_at`, `salary_from`, `area`, `type`, `website` |
| `CompanyVacanciesCountSerializer` | `serializers.Serializer` | Отчёт №1 | `name` (`CharField`), `vacancies` (`IntegerField`) |
| `ReportRowSerializer` | `serializers.Serializer` | Строка отчёта о вакансии (отчёты №2, №4, №5) | `company` (`CharField`), `name`, `salary_from` (`IntegerField(allow_null=True)`), `website` (необязательный) |
| `AvgSalarySerializer` | `serializers.Serializer` | Отчёт №3 | `name`, `avg_salary` (`IntegerField(allow_null=True)`) |
| `LoadResultSerializer` | `serializers.Serializer` | Ответ о загрузке данных | `message`, `companies` (опц.), `vacancies` (опц.) |
| `DatabaseCreateSerializer` | `serializers.Serializer` | Ответ о создании БД | `message` |

Используемые классы DRF:
- `serializers.ModelSerializer` — авто-сериализатор по модели Django;
- `serializers.Serializer` — ручной сериализатор;
- поля `CharField`, `IntegerField` (в т.ч. `allow_null=True`, `required=False`, `read_only=True`, `allow_blank=True`);
- вложенный сериализатор `company = CompanySerializer(read_only=True)`.

---

## 8. REST API представления — `hh_parser/api_views.py`

Все классы наследуют `rest_framework.views.APIView`. GET-эндпоинты отдают отчёты через сериализаторы, POST-эндпоинты выполняют действия с БД.

| Класс | Метод | URL | Назначение |
| --- | --- | --- | --- |
| `ApiRootView` | `get` | `/api/` | Справочник всех эндпоинтов (словарь `{имя: {"url", "description"}}`) |
| `CompaniesListView` | `get` | `/api/companies/` | Список компаний: `Company.objects.all()` → `CompanySerializer(many=True)` |
| `VacanciesListView` | `get` | `/api/vacancies/` | Все вакансии, либо поиск при наличии `?keyword=`; `Vacancy.objects.select_related("company")` — жадная загрузка FK |
| `CompaniesVacanciesCountView` | `get` | `/api/reports/companies-count/` | Отчёт №1 через `DBManager.get_companies_and_vacancies_count()` |
| `AllVacanciesView` | `get` | `/api/reports/all-vacancies/` | Отчёт №2 |
| `AvgSalaryView` | `get` | `/api/reports/avg-salary/` | Отчёт №3 |
| `HigherSalaryView` | `get` | `/api/reports/higher-salary/` | Отчёт №4 |
| `SearchVacanciesView` | `get` | `/api/reports/search/?keyword=` | Отчёт №5; без `keyword` — `400 BAD_REQUEST` |
| `DatabaseCreateView` | `post` | `/api/database/create/` | `DBWorker().create_database()` |
| `LoadTestDataView` | `post` | `/api/load/test-data/` | `DBWorker().save_test_data()`; ошибка → `400` |
| `LoadHHDataView` | `post` | `/api/load/hh/` | `DBWorker().load_companies_from_file()` + `.save_to_db()`; ошибка → `400` |

Используемые инструменты DRF:
- `APIView` + методы `get`/`post` — маршрутизация по HTTP-методам;
- `Response(data)` — DRF-ответ (рендерится в JSON или HTML Browsable API);
- `request.query_params.get("keyword", "")` — чтение GET-параметра;
- `status.HTTP_400_BAD_REQUEST` — код ошибки валидации;
- `serializer.data` / `serializer = X(data); Response(serializer.data)` — сериализация.

---

## 9. Представления шаблонов — `hh_parser/views.py`

View-функции (Django), реализующие HTML-интерфейс. Используют `django.shortcuts.render`.

| Функция | URL | Назначение |
| --- | --- | --- |
| `index(request)` | `/` | Главное меню, рендерит `index.html` |
| `create_database(request)` | `/database/create/` | Пункт «1». POST — `DBWorker().create_database()`; результат через `_render_action` |
| `load_test_data(request)` | `/load/test-data/` | Пункт «2». POST — `save_test_data()`, ловится `TestDataError` |
| `load_hh_data(request)` | `/load/hh/` | Пункт «3». POST — чтение компаний из файла и `save_to_db()`, ловятся `HHApiError`/`TestDataError`; в GET показывает список компаний из файла |
| `report_companies_count(request)` | `/reports/companies-count/` | Отчёт №1 |
| `report_all_vacancies(request)` | `/reports/all-vacancies/` | Отчёт №2 |
| `report_avg_salary(request)` | `/reports/avg-salary/` | Отчёт №3 |
| `report_higher_salary(request)` | `/reports/higher-salary/` | Отчёт №4 |
| `report_search(request)` | `/reports/search/` | Отчёт №5: `keyword` из `request.GET`; `DBManager.get_vacancies_with_keyword(keyword)` только при непустом слове |
| `_render_action(request, title, message, error)` | — | Вспомогательная: рендер `action_result.html` |
| `_render_report(request, title, columns, rows)` | — | Вспомогательная: рендер `report.html` с колонками `[{"key", "label"}]` |

Используемые функции Django:
- `render(request, template, context)` — рендер шаблона с контекстом;
- `request.method` — проверка HTTP-метода (`POST`/`GET`);
- `request.GET.get("keyword", "")` — чтение GET-параметра.

---

## 10. Теги шаблонов — `hh_parser/templatetags/hh_filters.py`

```python
register = template.Library()
```
Регистрация библиотеки пользовательских шаблонных фильтров.

- **`get_item(mapping, key)`** — фильтр `{{ row|get_item:col.key }}`: возвращает `mapping.get(key)` — чтение значения словаря по ключу в шаблоне.
- **`format_salary(salary)`** — фильтр `{{ value|format_salary }}`: форматирует зарплату.
  - `None` → `"Нет данных"`;
  - иначе `f"{salary:,}".replace(",", " ")` — разделитель тысяч пробелом (например, `226250` → `226 250`).
  - Использует: f-строку, `str.replace`.

---

## 11. Management-команды

Каталог `hh_parser/management/commands/`. Каждая команда — класс `Command(BaseCommand)` с переопределённым `handle` (консольный аналог соответствующего пункта меню).

| Команда | Класс/`handle` | Назначение |
| --- | --- | --- |
| `create_database` | `Command.handle(self, *args, **options)` | `DBWorker().create_database()`; затем `call_command("migrate")` — применение миграций |
| `load_test_data` | `Command.handle(...)` | `DBWorker().save_test_data()`; перехват `TestDataError` |
| `load_hh_data` | `Command.handle(...)` | `load_companies_from_file()` + `save_to_db()`; перехват `HHApiError` |

Используемые инструменты Django:
- `BaseCommand` с атрибутом `help` — метаданные команды;
- `self.stdout.write(self.style.SUCCESS(text))` — вывод в stdout (зелёный);
- `self.stderr.write(self.style.ERROR(text))` — вывод ошибки в stderr;
- `call_command("migrate", verbosity=1)` — программный вызов другой management-команды.

---

## 12. Тесты — `hh_parser/tests.py`

Тесты на базе `django.test.TestCase` (каждый `TestCase` изолирован транзакцией).

- **`_load_fixture()`** — вспомогательная функция: создаёт компании и вакансии напрямую через ORM из словаря `TEST_DATA` (компании `Яндекс`, `VK` и 3 вакансии).

### `DBWorkerTest`
| Метод | Что проверяет |
| --- | --- |
| `test_validate_test_data_ok` | Валидация корректной структуры проходит без ошибок |
| `test_validate_test_data_missing_field` | При отсутствии поля `area` поднимается `TestDataError` с номером записи и именем поля |
| `test_save_test_data` | Мок `read_test_data`; после `save_test_data()` в БД 2 компании и 3 вакансии |

### `DBManagerTest` (fixture: `_load_fixture()`)
| Метод | Что проверяет |
| --- | --- |
| `test_companies_and_vacancies_count` | Возвращается 2 строки |
| `test_all_vacancies_excludes_null_salary` | Вакансии без зарплаты (`None`) исключаются |
| `test_avg_salary` | Средняя зарплата корректна (180000 и 200000) |
| `test_vacancies_with_higher_salary` | Выше средней — только `Java Developer` |
| `test_vacancies_with_keyword` | Поиск «python» находит `Python Developer` |

### `ApiTest`
| Метод | Что проверяет |
| --- | --- |
| `test_companies_list` | `GET /api/companies/` → 200, 2 записи |
| `test_vacancies_search` | `GET /api/vacancies/?keyword=python` → 200, 1 запись |
| `test_report_higher_salary` | `GET /api/reports/higher-salary/` → 200, 1 запись |
| `test_search_requires_keyword` | `GET /api/reports/search/` без ключевого слова → 400 |

### `TemplateViewTest`
| Метод | Что проверяет |
| --- | --- |
| `test_index_page` | Главная страница содержит текст меню |
| `test_report_avg_salary_page` | Страница отчёта №3 содержит отформатированное значение «180 000» |

Используемые инструменты тестирования:
- `django.test.TestCase`, `self.client.get/post` — тестовый HTTP-клиент;
- `unittest.mock.patch` — мокирование функций;
- `self.assertRaises`, `assertEqual`, `assertIn`, `assertNotIn`, `assertContains`.

---

## 13. Параметры конфигурации Django — `config/settings.py`

### Блоки настроек (краткие комментарии)
- `BASE_DIR` — корень проекта (`Path(__file__).resolve().parent.parent`).
- `load_dotenv()` — загрузка `.env`.
- `SECRET_KEY` — из окружения (или значение по умолчанию для разработки).
- `DEBUG`, `ALLOWED_HOSTS` — из окружения.
- `INSTALLED_APPS`:
  - стандартные приложения Django (`admin`, `auth`, `contenttypes`, `sessions`, `messages`, `staticfiles`);
  - `rest_framework` — Django REST Framework;
  - `hh_parser` — приложение проекта.
- `TEMPLATES` — `DIRS` указывает на корневой каталог `templates`; `APP_DIRS=True`.
- `DATABASES["default"]` — PostgreSQL: параметры `NAME`, `HOST`, `USER`, `PASSWORD`, `PORT` из переменных окружения.
- `LANGUAGE_CODE = "ru-ru"` — локаль интерфейса.
- `STATIC_URL = "static/"`, `STATICFILES_DIRS = [BASE_DIR / "static"]`.
- `DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"`.
- `REST_FRAMEWORK`:
  - `DEFAULT_RENDERER_CLASSES` — `JSONRenderer` + `BrowsableAPIRenderer` (браузерная документация API);
  - `DEFAULT_PAGINATION_CLASS = LimitOffsetPagination`, `PAGE_SIZE = 100` — пагинация по 100 записей.

---

## Сводная таблица: типовые используемые методы/функции

| Технология | Метод/функция | Где используется |
| --- | --- | --- |
| requests | `requests.get()`, `.json()`, `.status_code`, `RequestException` | `api_hh.py` |
| psycopg2 | `connect()`, `conn.cursor()`, `cur.execute()`, `fetchone()`, `autocommit` | `db_worker.create_database` |
| Django ORM | `objects.all/filter/order_by/values/annotate/aggregate/bulk_create/get_or_create/update_or_create/select_related/delete`, `F`, `Avg` | `db_worker.py`, `db_manager.py`, `api_views.py` |
| Django | `transaction.atomic()`, `render()`, `BaseCommand`, `call_command` | сервисы, views, команды |
| DRF | `APIView`, `Response`, `ModelSerializer`, `Serializer`, `status`, поля сериализаторов | `api_views.py`, `serializers.py` |
| stdlib | `json.load`, `time.sleep`, `os.getenv`, `Path`, f-строки | утилиты, API-сервис |
| Template | `register.filter`, `{{ value\|filter }}` | `hh_filters.py`, шаблоны |