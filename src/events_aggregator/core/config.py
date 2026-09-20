from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_host: str
    postgres_port: int
    postgres_username: str
    postgres_password: str
    postgres_database_name: str

    events_provider_url: str | None = None
    events_provider_api_key: str | None = None

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
