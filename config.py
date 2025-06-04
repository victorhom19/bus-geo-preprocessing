import os
import sys

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "app")

sys.path.append(SRC_PATH)

class Config(BaseSettings):

    # Конфигурация API
    FASTAPI_HOST: str
    FASTAPI_PORT: int

    # Конфигурация подключения к базе данных
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_URL: PostgresDsn

    PROCESS_POOL_WORKERS_NUM: int = 8


app_config = Config(_env_file=os.path.join(PROJECT_ROOT, '.env'))
