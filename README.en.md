# Parser Vacancies — HH.ru on Django REST Framework

A port of the console project **Proj_HH** to **Django REST Framework** while keeping all of the original functionality. User interaction is implemented in two ways:

- **HTML templates** — web pages for the menu, reports, and actions;
- **REST API** — Django REST Framework endpoints under the `/api/` prefix.

> **Note:** access to the hh.ru API may be restricted (403 Forbidden). As in the original project, an offline mode is provided that loads pre-prepared test data from `data/test_data.json`.

---

## Features (kept from Proj_HH)

Main menu:

1. **Create database** — creates the PostgreSQL database (tables are created via Django migrations);
2. **Load test data** — clears the tables and loads data from `data/test_data.json` (with JSON structure validation);
3. **Load data from HH.ru** — reads the company list from `data/companies.txt` and loads data through the hh.ru API;
4. Analytical reports:
   - list of companies and their vacancy counts;
   - all vacancies;
   - average salary per company;
   - vacancies with a salary higher than the average;
   - vacancy search by keyword.

---

## Project structure

```text
.
├── config/                        # Django settings
│   ├── settings.py                # PostgreSQL, DRF, templates
│   └── urls.py
├── hh_parser/                     # application
│   ├── api_urls.py                # REST API routes
│   ├── api_views.py               # DRF views
│   ├── serializers.py             # DRF serializers
│   ├── views.py                   # view functions for HTML pages
│   ├── models.py                  # Company, Vacancy
│   ├── admin.py
│   ├── services/
│   │   ├── api_hh.py              # APIhh counterpart (hh.ru API)
│   │   ├── db_worker.py           # DBWorker counterpart (DB + data loading)
│   │   └── db_manager.py          # DBManager counterpart (analytical queries)
│   ├── management/commands/       # create_database, load_test_data, load_hh_data
│   ├── templatetags/hh_filters.py # salary formatting
│   ├── templates/hh_parser/       # HTML templates
│   └── tests.py                   # tests
├── data/
│   ├── companies.txt
│   └── test_data.json
├── .env.example
├── DOCUMENTATION.md               # methods and functions reference, grouped by module
├── manage.py
├── README.md                      # documentation in Russian
├── README.en.md                   # documentation in English (this file)
└── requirements.txt
```

### Mapping to the original project

| Original Proj_HH module     | DRF project implementation                  |
| --------------------------- | ------------------------------------------- |
| `src/APIhh.py`              | `hh_parser/services/api_hh.py`              |
| `src/DBWorker.py`           | `hh_parser/services/db_worker.py`           |
| `src/DBManager.py`          | `hh_parser/services/db_manager.py`          |
| `src/user_interface.py`     | `hh_parser/views.py` + HTML templates       |
| `companies`, `vacancies` tables | `Company`, `Vacancy` models (same schema) |

The `HHApiError` and `TestDataError` exceptions are preserved.

---

## Project setup

```bash
# 1. Create a virtual environment and install dependencies
py -3.14 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. .env file
# Copy .env.example to .env and set your PostgreSQL connection details

# 3. Create the database and tables
python manage.py create_database

# 4. Start the server
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser — the application main menu.

### Loading data

```bash
python manage.py load_test_data   # test data (offline mode)
python manage.py load_hh_data     # data from hh.ru (if the API is available)
```

---

## REST API (Django REST Framework)

Interactive documentation is available on the API pages (Browsable API). The API root is `http://127.0.0.1:8000/api/` (endpoint reference).

| Method | Endpoint                                    | Description                                    |
| ------ | ------------------------------------------- | ---------------------------------------------- |
| GET    | `/api/companies/`                           | List of companies                              |
| GET    | `/api/vacancies/`                           | List of vacancies                              |
| GET    | `/api/vacancies/?keyword=python`            | Search vacancies by keyword                    |
| GET    | `/api/reports/companies-count/`             | Companies and their vacancy counts             |
| GET    | `/api/reports/all-vacancies/`               | All vacancies                                  |
| GET    | `/api/reports/avg-salary/`                  | Average salary per company                     |
| GET    | `/api/reports/higher-salary/`               | Vacancies with salary higher than the average  |
| GET    | `/api/reports/search/?keyword=Data`         | Search vacancies by keyword                    |
| POST   | `/api/database/create/`                     | Create the database                            |
| POST   | `/api/load/test-data/`                      | Load test data                                 |
| POST   | `/api/load/hh/`                             | Load data from hh.ru                           |

Example response:

```json
GET /api/reports/avg-salary/
[
  {"name": "T-Bank", "avg_salary": 226250},
  {"name": "Ozon",   "avg_salary": 212000}
]
```

---

## HTML templates

UI templates (`hh_parser/templates/hh_parser/`):

- `base.html` — the common page skeleton;
- `index.html` — the main menu (actions 1–3 and reports);
- `action_result.html` — the result of "Create database" / "Load test data";
- `load_hh.html` — the hh.ru data loading page (company list from the file);
- `report.html` — a generic report table;
- `search.html` — the keyword search form.

---

## Code documentation

The document `DOCUMENTATION.md` contains comments for every method and function used in the project, grouped by module: models, services, utilities, serializers, API and template views, template tags, management commands, tests, and Django settings.

---

## Tests

```bash
python manage.py test hh_parser
```

Coverage: test data validation and loading, analytical queries, DRF endpoints, template pages.

---

## Error handling

As in the original project:

- hh.ru API errors (`HHApiError`) — reported without a crash;
- test data errors (`TestDataError`) — required fields are validated before the tables are cleared, and loading runs inside a transaction;
- when hh.ru is unavailable, the application works in offline mode using test data.

---

Author: Ivan Glushenkov. Study project on Django REST Framework, PostgreSQL, and SQL.