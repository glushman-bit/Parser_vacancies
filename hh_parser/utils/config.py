import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Параметры подключения к PostgreSQL из переменных окружения (.env).

    Единый источник для Django (settings.DATABASES) и сервисов
    (psycopg2-подключения в DBWorker). Значения по умолчанию защищают
    от None, если переменная не задана в .env.
    """

    POSTGRES_NAME = os.getenv("POSTGRES_NAME", "headhunter_drf")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

    DB_PARAMS = {
        "host": POSTGRES_HOST,
        "user": POSTGRES_USER,
        "password": POSTGRES_PASSWORD,
        "port": POSTGRES_PORT,
    }
