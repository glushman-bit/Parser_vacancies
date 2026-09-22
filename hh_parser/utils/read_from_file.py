import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

path_file = DATA_DIR / "companies.txt"
test_data_file = DATA_DIR / "test_data.json"


def read_companies_from_file(file_path):
    """Чтение списка компаний из файла."""
    with open(file_path, "r", encoding="utf-8") as f:
        return [
            line.strip()
            for line in f
            if line.strip()
        ]


def read_test_data(file_path):
    """Чтение тестовых данных из JSON-файла."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
