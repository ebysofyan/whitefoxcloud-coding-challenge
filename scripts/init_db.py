"""Initialise the DynamoDB `Books` table.

Usage: `make db-init`. Requires DynamoDB Local running (`make db`) or AWS creds.
"""

import os
import sys
from pathlib import Path

# Ensure project root on sys.path so `src` package imports work when invoked
# as a plain script (`python scripts/init_db.py`).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# DynamoDB Local accepts any credentials, but boto3 will hang searching for
# real credentials if none are present in the environment. Provide dummies.
os.environ.setdefault("AWS_ACCESS_KEY_ID", "local")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "local")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")

import boto3  # noqa: E402

from src.config import settings  # noqa: E402

kwargs: dict[str, object] = {"region_name": settings.aws_region}
if settings.dynamodb_endpoint:
    kwargs["endpoint_url"] = settings.dynamodb_endpoint

dynamodb = boto3.resource("dynamodb", **kwargs)

try:
    dynamodb.create_table(
        TableName=settings.books_table_name,
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    print(f"Table created: {settings.books_table_name}")
except dynamodb.meta.client.exceptions.ResourceInUseException:
    print(f"Table already exists: {settings.books_table_name}")
