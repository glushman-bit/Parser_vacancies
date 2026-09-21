# Parser Vacancies — HH.ru на Django REST Framework

Перевод консольного проекта **Proj_HH** на **Django REST Framework** с сохранением всей исходной функциональности. Взаимодействие с пользователем реализовано двумя способами:

- **HTML-шаблоны** — веб-страницы меню, отчётов и действий;
- **REST API** — эндпоинты Django REST Framework по префиксу `/api/`.

> **Примечание:** доступ к API hh.ru может быть ограничен (403 Forbidden). Как и в исходном проекте, предусмотрен режим загрузки заранее подготовленных тестовых данных из `data/test_data.json`.

---

## Функциональность (сохранена из Proj_HH)

Главное меню:

1. **Создать базу данных** — создание БД PostgreSQL (таблицы — через миграции Django);
2. **Загрузить тестовые данные** — очистка таблиц и загрузка данных из `data/test_data.json` (с проверкой структуры JSON);
3. **Загрузить данные с HH.ru** — чтение списка компаний из `data/companies.txt` и загрузка через API hh.ru;
4. Аналитические отчёты:
   - список компаний и количество вакансий;
   - все вакансии;
   - средняя зарплата по компаниям;
   - вакансии с зарплатой выше средней;
   - поиск вакансий по ключевому слову.

---

## Структура проекта

```text
.
├── config/                        # настройки Django
│   ├── settings.py                # PostgreSQL, DRF, шаблоны
│   └── urls.py
├── hh_parser/                     # приложение
│   ├── api_urls.py                # маршруты REST API
│   ├── api_views.py               # DRF-представления
│   ├── serializers.py             # DRF-сериализаторы
│   ├── views.py                   # view-функции для HTML-страниц
│   ├── models.py                  # Company, Vacancy
│   ├── admin.py
│   ├── services/
│   │   ├── api_hh.py              # аналог APIhh (работа с API hh.ru)
│   │   ├── db_worker.py           # аналог DBWorker (БД и загрузка данных)
│   │   └── db_manager.py          # аналог DBManager (аналитические запросы)
│   ├── management/commands/       # create_database, load_test_data, load_hh_data
│   ├── templatetags/hh_filters.py # форматирование зарплаты
│   ├── templates/hh_parser/       # HTML-шаблоны
│   └── tests.py                   # тесты
├── data/
│   ├── companies.txt
│   └── test_data.json
├── .env.example
├── DOCUMENTATION.md          # справка по методам и функциям по модулям
├── manage.py
├── README.md                 # документация на русском
├── README.en.md              # документация на английском
└── requirements.txt
```

### Соответствие исходному проекту

| Исходный модуль Proj_HH     | Реализация в DRF-проекте                       |
| --------------------------- | ---------------------------------------------- |
| `src/APIhh.py`              | `hh_parser/services/api_hh.py`                 |
| `src/DBWorker.py`           | `hh_parser/services/db_worker.py`              |
| `src/DBManager.py`          | `hh_parser/services/db_manager.py`             |
| `src/user_interface.py`     | `hh_parser/views.py` + HTML-шаблоны            |
| таблицы `companies`, `vacancies` | модели `Company`, `Vacancy` (та же схема) |

Исключения `HHApiError` и `TestDataError` сохранены.

---

## Настройка проекта

```bash
# 1. Создание виртуального окружения и установка зависимостей
py -3.14 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Файл .env
# Скопируйте .env.example в .env и укажите параметры подключения к PostgreSQL

# 3. Создание базы данных и таблиц
python manage.py create_database

# 4. Запуск сервера
python manage.py runserver
```

Откройте в браузере `http://127.0.0.1:8000/` — главное меню приложения.

### Загрузка данных

```bash
python manage.py load_test_data   # тестовые данные (автономный режим)
python manage.py load_hh_data     # данные с hh.ru (при доступности API)
```

---

## REST API (Django REST Framework)

Браузерная документация доступна на страницах API (Browsable API). Корень API: `http://127.0.0.1:8000/api/` (справочник всех эндпоинтов).

| Метод | Endpoint                                    | Описание                                     |
| ----- | ------------------------------------------- | -------------------------------------------- |
| GET   | `/api/companies/`                           | Список компаний                              |
| GET   | `/api/vacancies/`                           | Список вакансий                              |
| GET   | `/api/vacancies/?keyword=python`            | Поиск вакансий по ключевому слову            |
| GET   | `/api/reports/companies-count/`             | Компании и количество вакансий               |
| GET   | `/api/reports/all-vacancies/`               | Все вакансии                                 |
| GET   | `/api/reports/avg-salary/`                  | Средняя зарплата по компаниям                |
| GET   | `/api/reports/higher-salary/`               | Вакансии с зарплатой выше средней            |
| GET   | `/api/reports/search/?keyword=Data`         | Поиск вакансий по ключевому слову            |
| POST  | `/api/database/create/`                     | Создание базы данных                         |
| POST  | `/api/load/test-data/`                      | Загрузка тестовых данных                     |
| POST  | `/api/load/hh/`                             | Загрузка данных с hh.ru                      |

Пример ответа:

```json
GET /api/reports/avg-salary/
[
  {"name": "Т-Банк", "avg_salary": 226250},
  {"name": "Ozon",   "avg_salary": 212000}
]
```

---

## HTML-шаблоны

Шаблоны интерфейса (`hh_parser/templates/hh_parser/`):

- `base.html` — общий каркас страницы;
- `index.html` — главное меню (действия 1–3 и отчёты);
- `action_result.html` — результат действия «Создать базу данных» / «Загрузить тестовые данные»;
- `load_hh.html` — страница загрузки данных с hh.ru (список компаний из файла);
- `report.html` — универсальная таблица отчётов;
- `search.html` — форма поиска вакансий по ключевому слову.

---

## Тесты

```bash
python manage.py test hh_parser
```

Покрытие: валидация и загрузка тестовых данных, аналитические запросы, DRF-endpoints, страницы шаблонов.

---

## Документация по коду

Файл `DOCUMENTATION.md` содержит комментарии ко всем используемым в проекте методам и функциям, сгруппированные по модулям: модели, сервисы, утилиты, сериализаторы, представления API и шаблонов, теги шаблонов, management-команды, тесты и настройки Django.

---

## Обработка ошибок

Как и в исходном проекте:

- ошибки API hh.ru (`HHApiError`) — вывод без аварийного завершения;
- ошибки тестовых данных (`TestDataError`) — проверка обязательных полей до очистки таблиц, загрузка в транзакции;
- при недоступности hh.ru приложение работает в автономном режиме с тестовыми данными.

---

Автор: Ivan Glushenkov. Учебный проект по Django REST Framework, PostgreSQL и SQL.