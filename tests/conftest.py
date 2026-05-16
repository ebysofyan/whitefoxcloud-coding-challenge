import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

from src.auth import token_store
from src.config import settings
from src.main import app


@pytest.fixture(autouse=True)
def _isolate_settings(monkeypatch):
    """Strip any local DynamoDB endpoint so moto mocks intercept boto3."""
    monkeypatch.setattr(settings, "dynamodb_endpoint", None)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", settings.aws_region)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def aws_mock():
    mock = mock_aws()
    mock.start()
    yield mock
    mock.stop()


@pytest.fixture
def dynamodb_table(aws_mock):
    dynamodb = boto3.resource("dynamodb", region_name=settings.aws_region)
    table = dynamodb.create_table(
        TableName=settings.books_table_name,
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    return table


@pytest.fixture
def auth_token():
    return token_store.create_token("admin")
