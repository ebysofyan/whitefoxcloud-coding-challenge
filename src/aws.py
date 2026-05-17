from typing import Any

import boto3

from src.config import settings


def get_dynamodb_resource() -> boto3.resources.base.ServiceResource:
    """Create a shared DynamoDB resource with endpoint auto-detection."""
    kwargs: dict[str, Any] = {"region_name": settings.aws_region}
    if settings.dynamodb_endpoint:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint
    return boto3.resource("dynamodb", **kwargs)
