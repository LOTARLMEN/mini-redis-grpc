from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT_DIR / ".env"


class GRPCServer(BaseModel):
    HOST: str = "localhost"
    PORT: str = "50051"

    @property
    def SERVER_URL(self):
        return f"{self.HOST}:{self.PORT}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_nested_delimiter="__",
        env_ignore_empty=True,
    )

    server: GRPCServer = GRPCServer()


settings = Settings()
