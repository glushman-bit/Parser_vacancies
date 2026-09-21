import time

import requests


class HHApiError(Exception):
    """Ошибка при работе с API hh.ru."""


class APIhh:
    """Класс для работы с сайтом API hh.ru."""

    def __init__(self) -> None:
        self.base_url = "https://api.hh.ru"
        self.headers = {"User-Agent": "hh_api_db/1.0"}

    def get_employers(self, employer_name: list[str]):
        """Получение данных работодателя."""
        employers_data = []

        for name in employer_name:
            params = {"text": name, "only_with_vacancies": True, "type": "company", "area": 113}

            try:
                response = requests.get(f"{self.base_url}/employers", params=params, headers=self.headers)

            except requests.RequestException as e:
                raise HHApiError(f"Не удалось подключиться к API hh.ru: {e}") from e

            if response.status_code != 200:
                raise HHApiError(f"API hh.ru вернул ошибку: {response.status_code}")

            items = response.json().get("items")

            if items:
                employers_data.append(items[0])

            else:
                raise HHApiError(f"Ошибка запроса: {response.status_code}")

            time.sleep(0.2)

        return employers_data

    def get_vacancies(self, employer_id: str):
        """Получение данных о вакансиях по работодателю."""
        params = {"employer_id": employer_id, "per_page": 30}

        try:
            response = requests.get(f"{self.base_url}/vacancies", params=params, headers=self.headers)

        except requests.RequestException as e:
            raise HHApiError(f"Не удалось подключиться к API hh.ru: {e}") from e

        if response.status_code != 200:
            raise HHApiError(f"API hh.ru вернул ошибку: {response.status_code}")

        return response.json().get("items", [])
