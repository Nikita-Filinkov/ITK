import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


MODULE_DIR = Path(__file__).parent
ENV_PATH = os.path.join(MODULE_DIR, ".env")


class Settings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: str

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")

    @property
    def get_redis_url(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


settings = Settings()

# print(settings.get_redis_url)
