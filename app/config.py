import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CasePilot"
    app_version: str = "0.1.0"
    database_path: str = os.getenv("DATABASE_PATH", "./data/casepilot.db")
    debug: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
