#!/usr/bin/env python3
"""Static baseline checks for the Mechenz sample."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ".gitignore",
    "CHANGES.md",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "VISION.md",
    "requirements.txt",
    "settings.py.example",
    "docs/plans/2026-06-08-mechenz-baseline.md",
    "docs/plans/2026-06-08-mechenz-modernization.md",
    "docs/plans/2026-06-08-python3-scraper-baseline.md",
    "docs/plans/2026-06-08-scrape-settings-validation.md",
    "docs/plans/2026-06-09-mail-settings-validation.md",
    "docs/plans/2026-06-09-mail-recipient-normalization.md",
    "tests/test_main.py",
    "tests/test_royal_mail.py",
    "tests/test_royalmail.py",
]
SECRET_PATTERNS = [
    re.compile(r"smtp_password\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE),
    re.compile(r"SMTP_PASSWORD\s*=\s*[^ \n]+"),
]


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        for path in missing:
            print(f"missing required file: {path}", file=sys.stderr)
        return 1

    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.suffix in {".pyc", ".pyo"}:
            print(f"compiled Python artifact found: {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        if path.is_dir() or "__pycache__" in path.parts:
            continue
        if path.suffix not in {".py", ".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                print(f"possible committed SMTP secret in {path.relative_to(ROOT)}", file=sys.stderr)
                return 1

    main_source = (ROOT / "main.py").read_text(encoding="utf-8")
    mail_source = (ROOT / "RoyalMail.py").read_text(encoding="utf-8")
    test_main = (ROOT / "tests/test_main.py").read_text(encoding="utf-8")
    test_mail = (ROOT / "tests/test_royal_mail.py").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    vision = (ROOT / "VISION.md").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    changes = (ROOT / "CHANGES.md").read_text(encoding="utf-8")
    settings_plan = (ROOT / "docs/plans/2026-06-08-scrape-settings-validation.md").read_text(encoding="utf-8")
    mail_plan = (ROOT / "docs/plans/2026-06-09-mail-settings-validation.md").read_text(encoding="utf-8")
    recipient_plan = (ROOT / "docs/plans/2026-06-09-mail-recipient-normalization.md").read_text(encoding="utf-8")

    checks = [
        ("empty required settings" in main_source and "required_values" in main_source,
         "load_scrape_settings must reject blank required settings"),
        ("test_load_scrape_settings_rejects_blank_required_values" in test_main,
         "tests must cover blank scrape settings validation"),
        ("scrape settings validation" in readme.lower()
         and "scrape settings validation" in vision.lower()
         and "scrape settings validation" in security.lower(),
         "docs must mention scrape settings validation"),
        ("scrape settings validation" in changes.lower(),
         "CHANGES must record scrape settings validation"),
        ("status: completed" in settings_plan,
         "scrape settings validation plan must be marked completed"),
        ("_parse_int_setting" in mail_source and "_parse_float_setting" in mail_source,
         "RoyalMail must sanitize numeric SMTP setting parsing"),
        ("invalid SMTP_PORT" in test_mail and "invalid SMTP_TIMEOUT" in test_mail,
         "tests must cover invalid numeric SMTP settings"),
        ("smtp numeric setting validation" in readme.lower()
         and "smtp numeric setting validation" in vision.lower()
         and "smtp numeric setting validation" in security.lower(),
         "docs must mention SMTP numeric setting validation"),
        ("smtp numeric setting validation" in changes.lower(),
         "CHANGES must record SMTP numeric setting validation"),
        ("status: completed" in mail_plan,
         "SMTP numeric setting validation plan must be marked completed"),
        ("str(address).strip()" in mail_source and "if not recipients" in mail_source,
         "RoyalMail must normalize and reject blank SMTP recipients"),
        ("test_send_mail_normalizes_recipients" in test_mail
         and "test_send_mail_rejects_blank_recipients" in test_mail,
         "tests must cover SMTP recipient normalization"),
        ("smtp recipient normalization" in readme.lower()
         and "smtp recipient normalization" in vision.lower()
         and "smtp recipient normalization" in security.lower(),
         "docs must mention SMTP recipient normalization"),
        ("smtp recipient normalization" in changes.lower(),
         "CHANGES must record SMTP recipient normalization"),
        ("status: completed" in recipient_plan,
         "SMTP recipient normalization plan must be marked completed"),
    ]
    for passed, message in checks:
        if not passed:
            print(message, file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
