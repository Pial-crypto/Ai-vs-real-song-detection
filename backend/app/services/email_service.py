"""Email service abstraction (SMTP / console fallback)."""

from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import List, Optional

from backend.app.config import get_settings
from backend.app.logging_config import get_logger

logger = get_logger("app.services.email")


@dataclass
class EmailConfig:
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    use_tls: bool = True
    from_address: str = "noreply@example.com"


class EmailService:
    def __init__(self, config: Optional[EmailConfig] = None) -> None:
        self.config = config or EmailConfig()
        settings = get_settings()
        self.config.smtp_host = getattr(settings, "smtp_host", self.config.smtp_host) if hasattr(settings, "smtp_host") else self.config.smtp_host

    def send(self, to: List[str], subject: str, body: str, html: bool = False) -> bool:
        msg = EmailMessage()
        msg["From"] = self.config.from_address
        msg["To"] = ", ".join(to)
        msg["Subject"] = subject
        if html:
            msg.add_alternative(body, subtype="html")
        else:
            msg.set_content(body)

        # Console fallback when no SMTP configured
        if not self.config.smtp_host or self.config.smtp_host == "localhost":
            logger.info("Email (console fallback)", extra={"to": to, "subject": subject, "body": body[:200]})
            return True

        try:
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port, timeout=10) as server:
                if self.config.use_tls:
                    server.starttls()
                if self.config.smtp_user and self.config.smtp_password:
                    server.login(self.config.smtp_user, self.config.smtp_password)
                server.send_message(msg)
            logger.info("Email sent", extra={"to": to, "subject": subject})
            return True
        except Exception as exc:
            logger.error("Email send failed", extra={"error": str(exc)})
            return False

    def send_welcome(self, to: str, username: str) -> bool:
        body = f"Hello {username},\n\nWelcome to AI vs Real Song Detection.\n\nBest regards,\nThe Team"
        return self.send([to], "Welcome!", body)

    def send_password_reset(self, to: str, reset_link: str) -> bool:
        body = f"Reset your password using the link: {reset_link}"
        return self.send([to], "Password Reset", body)

    def send_prediction_complete(self, to: str, filename: str, result: str) -> bool:
        body = f"Prediction complete for {filename}. Result: {result}"
        return self.send([to], "Prediction Complete", body)


def get_email_service() -> EmailService:
    return EmailService()
