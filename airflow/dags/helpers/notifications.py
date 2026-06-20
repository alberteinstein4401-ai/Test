"""Email notification operations using AWS SES."""
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import boto3

from .config import get_env


def send_report_email(report_path: Path) -> None:
    """Send report file as email attachment via AWS SES."""
    aws_region = get_env("AWS_REGION")
    sender = get_env("SES_SENDER")

    recipients_env = os.environ.get("SES_RECIPIENTS")
    if not recipients_env:
        raise ValueError("Missing required environment variable: SES_RECIPIENTS")

    recipients = [
        recipient.strip()
        for recipient in recipients_env.split(",")
        if recipient.strip()
    ]
    if not recipients:
        raise ValueError("SES_RECIPIENTS must contain at least one email address")

    subject = get_env(
        "SES_SUBJECT",
        "Lesson Completion Report",
    )

    with report_path.open("rb") as attachment_file:
        attachment_data = attachment_file.read()

    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.attach(
        MIMEText(
            "Please find attached the lesson completion report.",
            "plain",
        )
    )

    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(attachment_data)
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        f"attachment; filename={report_path.name}",
    )
    message.attach(attachment)

    client = boto3.client(
        "ses",
        region_name=aws_region,
    )
    client.send_raw_email(
        Source=sender,
        Destinations=recipients,
        RawMessage={"Data": message.as_string()},
    )
