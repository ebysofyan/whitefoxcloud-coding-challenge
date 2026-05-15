from src.config import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.books_table_name == "dev-books"
    assert settings.aws_region == "us-east-1"
    assert settings.environment == "dev"
