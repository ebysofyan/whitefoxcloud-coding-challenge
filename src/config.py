from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class TableConfig(BaseModel):
    books: str = "books"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        extra="ignore",
    )

    aws_region: str = "ap-southeast-1"
    environment: str = "dev"
    dynamodb_endpoint: str | None = None
    trust_proxy_headers: bool = False
    tables: TableConfig = TableConfig()

    @property
    def books_table_name(self) -> str:
        return f"{self.environment}-{self.tables.books}"


settings = Settings()
