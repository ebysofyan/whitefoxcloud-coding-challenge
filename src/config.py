from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    books_table_name: str = "dev-books"
    aws_region: str = "us-east-1"
    environment: str = "dev"
    model_config = {"env_prefix": "", "env_file": ".env", "extra": "ignore"}


settings = Settings()
