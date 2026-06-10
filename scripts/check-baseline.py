#!/usr/bin/env python3
"""Static baseline checks for the Mechenz sample."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ".gitignore",
    ".github/workflows/check.yml",
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
    "docs/plans/2026-06-09-make-gate-targets.md",
    "docs/plans/2026-06-09-robot-setting-validation.md",
    "docs/plans/2026-06-09-scrape-url-validation.md",
    "docs/plans/2026-06-09-smtp-header-validation.md",
    "docs/plans/2026-06-10-scrape-encoding-validation.md",
    "docs/plans/2026-06-10-hosted-python-validation.md",
    "docs/plans/2026-06-10-smtp-numeric-bounds.md",
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
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    settings_plan = (ROOT / "docs/plans/2026-06-08-scrape-settings-validation.md").read_text(encoding="utf-8")
    mail_plan = (ROOT / "docs/plans/2026-06-09-mail-settings-validation.md").read_text(encoding="utf-8")
    recipient_plan = (ROOT / "docs/plans/2026-06-09-mail-recipient-normalization.md").read_text(encoding="utf-8")
    make_gates_plan = (ROOT / "docs/plans/2026-06-09-make-gate-targets.md").read_text(encoding="utf-8")
    robot_plan = (ROOT / "docs/plans/2026-06-09-robot-setting-validation.md").read_text(encoding="utf-8")
    url_plan = (ROOT / "docs/plans/2026-06-09-scrape-url-validation.md").read_text(encoding="utf-8")
    header_plan = (ROOT / "docs/plans/2026-06-09-smtp-header-validation.md").read_text(encoding="utf-8")
    encoding_plan = (ROOT / "docs/plans/2026-06-10-scrape-encoding-validation.md").read_text(encoding="utf-8")
    hosted_validation_plan = (ROOT / "docs/plans/2026-06-10-hosted-python-validation.md").read_text(encoding="utf-8")
    numeric_bounds_plan = (ROOT / "docs/plans/2026-06-10-smtp-numeric-bounds.md").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/check.yml").read_text(encoding="utf-8")

    checks = [
        ("status: completed" in hosted_validation_plan and "make check" in hosted_validation_plan,
         "hosted Python validation plan must be marked completed"),
        ("permissions:\n  contents: read" in workflow
         and "cancel-in-progress: true" in workflow
         and "runs-on: ubuntu-24.04" in workflow
         and "timeout-minutes: 10" in workflow
         and "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10" in workflow
         and "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405" in workflow
         and 'python-version: "3.12"' in workflow
         and "cache-dependency-path: requirements.txt" in workflow
         and "python -m pip install --requirement requirements.txt" in workflow
         and "python -m pip check" in workflow
         and "run: make check" in workflow,
         "Check workflow must stay pinned, read-only, bounded, and dependency-aware"),
        (".PHONY: build check clean compile fmt lint static-check test" in makefile
         and "check: clean lint test build" in makefile
         and "lint: static-check" in makefile
         and "build: compile" in makefile,
         "Makefile must expose standard lint, test, build, and check gates"),
        ("make lint" in readme and "make test" in readme and "make build" in readme,
         "README must document standard Make gates"),
        ("make lint" in vision and "make test" in vision and "make build" in vision,
         "VISION must document standard Make gates"),
        ("make lint" in changes and "make test" in changes and "make build" in changes,
         "CHANGES must record standard Make gates"),
        ("status: completed" in make_gates_plan,
         "Make gate targets plan must be marked completed"),
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
        ("_valid_http_url" in main_source and "invalid scrape settings" in main_source,
         "load_scrape_settings must validate scrape URL schemes"),
        ("test_load_scrape_settings_rejects_invalid_scrape_urls" in test_main
         and "file:///tmp/private.html" in test_main
         and "not-a-url" in test_main,
         "tests must cover invalid scrape URL validation"),
        ("scrape url validation" in readme.lower()
         and "scrape url validation" in vision.lower()
         and "scrape url validation" in security.lower(),
         "docs must mention scrape URL validation"),
        ("scrape url validation" in changes.lower(),
         "CHANGES must record scrape URL validation"),
        ("status: completed" in url_plan,
         "scrape URL validation plan must be marked completed"),
        ("_parse_encoding_setting" in main_source
         and "codecs.lookup(encoding)" in main_source
         and "test_load_scrape_settings_rejects_invalid_encoding" in test_main
         and "not-a-codec" in test_main,
         "load_scrape_settings must validate configured scrape encodings"),
        ("scrape encoding validation" in readme.lower()
         and "scrape encoding validation" in vision.lower()
         and "scrape encoding validation" in security.lower(),
         "docs must mention scrape encoding validation"),
        ("scrape encoding validation" in changes.lower(),
         "CHANGES must record scrape encoding validation"),
        ("status: completed" in encoding_plan,
         "scrape encoding validation plan must be marked completed"),
        ("_parse_int_setting" in mail_source and "_parse_float_setting" in mail_source,
         "RoyalMail must sanitize numeric SMTP setting parsing"),
        ("maximum=65535" in mail_source
         and "maximum=300.0" in mail_source
         and "math.isfinite(parsed)" in mail_source,
         "RoyalMail must bound SMTP ports and require finite bounded timeouts"),
        ("invalid SMTP_PORT" in test_mail and "invalid SMTP_TIMEOUT" in test_mail,
         "tests must cover invalid numeric SMTP settings"),
        ("test_load_mail_settings_rejects_port_outside_tcp_range" in test_mail
         and "test_load_mail_settings_rejects_unbounded_timeout" in test_mail
         and "test_load_mail_settings_accepts_numeric_upper_bounds" in test_mail
         and '"65536"' in test_mail
         and '"nan", "inf", "301"' in test_mail,
         "tests must cover SMTP port and timeout upper bounds"),
        ("smtp numeric setting validation" in readme.lower()
         and "smtp numeric setting validation" in vision.lower()
         and "smtp numeric setting validation" in security.lower(),
         "docs must mention SMTP numeric setting validation"),
        ("smtp numeric setting validation" in changes.lower(),
         "CHANGES must record SMTP numeric setting validation"),
        ("status: completed" in mail_plan,
         "SMTP numeric setting validation plan must be marked completed"),
        ("status: completed" in numeric_bounds_plan
         and "65535" in numeric_bounds_plan
         and "300 seconds" in numeric_bounds_plan,
         "SMTP numeric bounds plan must be completed and document both limits"),
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
        ("_parse_bool_setting" in main_source
         and "invalid respect_robots" in test_main
         and "invalid MECHENZ_IGNORE_ROBOTS" in test_main,
         "tests must cover robot setting validation"),
        ("robot setting validation" in readme.lower()
         and "robot setting validation" in vision.lower()
         and "robot setting validation" in security.lower(),
         "docs must mention robot setting validation"),
        ("robot setting validation" in changes.lower(),
         "CHANGES must record robot setting validation"),
        ("status: completed" in robot_plan,
         "robot setting validation plan must be marked completed"),
        ("_validate_header_value" in mail_source
         and '_validate_header_value("SMTP_LOGIN", settings.login)' in mail_source
         and '_validate_header_value("SMTP_SUBJECT", subject)' in mail_source
         and '_validate_header_value("SMTP_RECIPIENT", recipient)' in mail_source
         and 'raise ValueError(f"invalid {name}")' in mail_source,
         "RoyalMail must reject CRLF in SMTP header values"),
        ("test_send_mail_rejects_header_newlines_before_smtp" in test_mail
         and "invalid SMTP_SUBJECT" in test_mail
         and "invalid SMTP_RECIPIENT" in test_mail
         and "invalid SMTP_LOGIN" in test_mail,
         "tests must cover SMTP header validation"),
        ("smtp header validation" in readme.lower()
         and "smtp header validation" in vision.lower()
         and "smtp header validation" in security.lower(),
         "docs must mention SMTP header validation"),
        ("smtp header validation" in changes.lower(),
         "CHANGES must record SMTP header validation"),
        ("status: completed" in header_plan,
         "SMTP header validation plan must be marked completed"),
    ]
    for passed, message in checks:
        if not passed:
            print(message, file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
