from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = "CosmosAI"
    app_version: str = "1.0.0"

    model_config = {"env_file": ".env"}


settings = Settings()
