# SMTP Numeric Setting Validation Plan

status: completed

## Context

`load_mail_settings` parsed `SMTP_PORT` and `SMTP_TIMEOUT` with bare `int` and
`float` conversions. Invalid values raised Python conversion errors that echoed
the raw configuration value back to callers.

## Objectives

- Parse SMTP port and timeout through named validation helpers.
- Reject invalid or non-positive numeric settings with stable field-name errors.
- Avoid echoing raw invalid configuration values in exceptions.
- Cover invalid port and timeout values with offline unit tests.
- Extend the static baseline and docs so the behavior stays visible.

## Verification

- `make check`
- `python3 -m unittest discover -s tests`
- `python3 scripts/check-baseline.py`
- `git diff --check`
