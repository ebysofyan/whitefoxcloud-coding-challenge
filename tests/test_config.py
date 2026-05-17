from src.config import Settings, TableConfig


def test_table_config_defaults():
    config = TableConfig()
    assert config.books == "books"


def test_settings_defaults(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    skip_vars = (
        "AWS_REGION",
        "ENVIRONMENT",
        "DYNAMODB_ENDPOINT",
        "TRUST_PROXY_HEADERS",
    )
    for var in skip_vars:
        monkeypatch.delenv(var, raising=False)
    settings = Settings(_env_file=None)
    assert settings.tables.books == "books"
    assert settings.books_table_name == "dev-books"
    assert settings.aws_region == "ap-southeast-1"
    assert settings.environment == "dev"
    assert settings.dynamodb_endpoint is None
    assert settings.trust_proxy_headers is False


def test_settings_env_prefixes_table_name(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for var in ("AWS_REGION", "ENVIRONMENT", "DYNAMODB_ENDPOINT"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("ENVIRONMENT", "prod")
    settings = Settings(_env_file=None)
    assert settings.books_table_name == "prod-books"


def test_settings_staging_env_prefixes_table_name(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for var in ("AWS_REGION", "ENVIRONMENT", "DYNAMODB_ENDPOINT"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("ENVIRONMENT", "staging")
    settings = Settings(_env_file=None)
    assert settings.books_table_name == "staging-books"
