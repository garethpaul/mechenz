"""SMTP notification helpers for Mechenz."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import math
import os
import smtplib
import ssl
from typing import Optional


@dataclass(frozen=True)
class MailSettings:
    login: str
    password: str
    host: str = "smtp.gmail.com"
    port: int = 587
    timeout: float = 10.0


def load_mail_settings(
    env: Mapping[str, str] = os.environ,
    settings_module: Optional[object] = None,
) -> MailSettings:
    login = _first_value(env.get("SMTP_LOGIN"), _module_value(settings_module, "smtp_login"))
    password = _first_value(env.get("SMTP_PASSWORD"), _module_value(settings_module, "smtp_password"))

    missing = []
    if not login:
        missing.append("SMTP_LOGIN")
    if not password:
        missing.append("SMTP_PASSWORD")
    if missing:
        raise ValueError("missing required SMTP configuration: " + ", ".join(missing))

    host = _first_value(env.get("SMTP_HOST"), _module_value(settings_module, "smtp_host"), "smtp.gmail.com")
    port = _parse_int_setting(
        "SMTP_PORT",
        _first_value(env.get("SMTP_PORT"), _module_value(settings_module, "smtp_port"), "587"),
        maximum=65535,
    )
    timeout = _parse_float_setting(
        "SMTP_TIMEOUT",
        _first_value(env.get("SMTP_TIMEOUT"), _module_value(settings_module, "smtp_timeout"), "10"),
        maximum=300.0,
    )

    return MailSettings(
        login=login,
        password=password,
        host=host,
        port=port,
        timeout=timeout,
    )


def send_mail(
    to: Iterable[str],
    subject: str,
    text: str,
    mail_settings: Optional[MailSettings] = None,
    smtp_factory: Callable[..., smtplib.SMTP] = smtplib.SMTP,
) -> None:
    settings = mail_settings or load_mail_settings()
    recipients = [
        str(address).strip()
        for address in to
        if address is not None and str(address).strip()
    ]
    if not recipients:
        raise ValueError("at least one recipient is required")
    _validate_header_value("SMTP_LOGIN", settings.login)
    _validate_header_value("SMTP_SUBJECT", subject)
    for recipient in recipients:
        _validate_header_value("SMTP_RECIPIENT", recipient)

    message = MIMEMultipart()
    message["From"] = settings.login
    message["To"] = COMMASPACE.join(recipients)
    message["Date"] = formatdate(localtime=True)
    message["Subject"] = subject
    message.attach(MIMEText(text, "plain", "utf-8"))

    tls_context = ssl.create_default_context()
    server = smtp_factory(settings.host, settings.port, timeout=settings.timeout)
    try:
        server.ehlo()
        server.starttls(context=tls_context)
        server.ehlo()
        server.login(settings.login, settings.password)
        refused = server.sendmail(settings.login, recipients, message.as_string())
        if refused:
            raise smtplib.SMTPRecipientsRefused(refused)
    except BaseException:
        try:
            server.close()
        except BaseException:
            pass
        raise
    else:
        server.close()


def sendMail(
    to,
    subject,
    text,
    server="smtp.gmail.com",
    settings_module: Optional[object] = None,
    smtp_factory: Callable[..., smtplib.SMTP] = smtplib.SMTP,
):
    """Compatibility wrapper for the original camelCase API."""
    settings = load_mail_settings(settings_module=settings_module)
    if server != "smtp.gmail.com":
        settings = MailSettings(
            login=settings.login,
            password=settings.password,
            host=server,
            port=settings.port,
            timeout=settings.timeout,
        )
    send_mail(to, subject, text, mail_settings=settings, smtp_factory=smtp_factory)


def _module_value(settings_module: Optional[object], name: str) -> Optional[str]:
    if settings_module is None:
        return None
    value = getattr(settings_module, name, None)
    if value is None:
        return None
    return str(value)


def _first_value(*values: Optional[str]) -> str:
    for value in values:
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _parse_int_setting(name: str, value: str, maximum: Optional[int] = None) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"invalid {name}") from None
    if parsed <= 0 or (maximum is not None and parsed > maximum):
        raise ValueError(f"invalid {name}")
    return parsed


def _parse_float_setting(name: str, value: str, maximum: Optional[float] = None) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"invalid {name}") from None
    if not math.isfinite(parsed) or parsed <= 0 or (maximum is not None and parsed > maximum):
        raise ValueError(f"invalid {name}")
    return parsed


def _validate_header_value(name: str, value: str) -> None:
    if "\r" in value or "\n" in value:
        raise ValueError(f"invalid {name}")


if __name__ == "__main__":
    recipient = os.environ.get("MECHENZ_TEST_RECIPIENT")
    if not recipient:
        raise SystemExit("MECHENZ_TEST_RECIPIENT is required for manual email testing")
    send_mail([recipient], "Mechenz test", "Body")
