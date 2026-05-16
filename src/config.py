from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env", extra="ignore")

    books_table_name: str = "dev-books"
    aws_region: str = "ap-southeast-1"
    environment: str = "dev"
    dynamodb_endpoint: str | None = None


settings = Settings()
