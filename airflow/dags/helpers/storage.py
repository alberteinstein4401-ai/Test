"""S3 storage operations."""
from pathlib import Path
from datetime import datetime as _dt
import re

import boto3

from .config import get_env


def upload_file_to_s3(report_path: Path) -> str:
    """Upload report file to S3 and return the S3 key.

    The upload will place the file under a date prefix (folder) so the S3
    object key looks like: <prefix>/<YYYY-MM-DD>/<filename>.
    The date is extracted from the report filename (expects
    `lesson_completion_report_{start}_{end}.csv`). If no date is found, the
    current date is used.
    """
    bucket = get_env("S3_REPORT_BUCKET")
    prefix = get_env("S3_REPORT_PREFIX", "reports")

    date_prefix = _dt.utcnow().strftime("%Y-%m-%d")

    s3_key = f"{prefix.rstrip('/')}/{date_prefix}/{report_path.name}"

    s3 = boto3.client(
        "s3",
        region_name=get_env("AWS_REGION"),
    )
    s3.upload_file(str(report_path), bucket, s3_key)
    return s3_key
