from src.config import Settings


def test_settings_defaults(monkeypatch, tmp_path):
    # Isolate from project .env so defaults reflect class-level values.
    monkeypatch.chdir(tmp_path)
    for var in (
        "BOOKS_TABLE_NAME",
        "AWS_REGION",
        "ENVIRONMENT",
        "DYNAMODB_ENDPOINT",
    ):
        monkeypatch.delenv(var, raising=False)
    settings = Settings(_env_file=None)
    assert settings.books_table_name == "dev-books"
    assert settings.aws_region == "us-east-1"
    assert settings.environment == "dev"
    assert settings.dynamodb_endpoint is None
