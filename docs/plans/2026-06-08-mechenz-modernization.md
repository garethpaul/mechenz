# Mechenz Modernization Plan

Status: completed
Completed: 2026-06-08

## Context

Mechenz was a Python 2-era scraper and email notification script. It depended
on a local `settings.py`, imported live-only dependencies at module import time,
ignored robots by default, and did not include tests or dependency metadata.

## Risks

- SMTP credentials could be committed accidentally through local settings files.
- Import-time mechanize, memcache, and SMTP configuration made local verification
  dependent on live services.
- The scraper ignored robots by default, which made target-site access behavior
  unsafe for a public sample.
- Cache updates happened before successful notification delivery, which could
  suppress retries after a mail failure.

## Work Completed

- Ported email imports, iteration, and type handling to Python 3-compatible code.
- Moved SMTP credentials to `SMTP_LOGIN` and `SMTP_PASSWORD`, while keeping a
  local `settings.py` fallback for legacy users.
- Moved mechanize and memcache imports behind runtime functions so unit tests can
  run with the Python standard library only.
- Added an HTML parser for `div.action span` extraction and tests for parser,
  cache, notification, and SMTP behavior.
- Changed notification flow to update memcache only after a successful send.
- Added `requirements.txt`, `.gitignore`, `Makefile`, and `scripts/check-baseline.py`.

## Verification

- `make check`
- `git diff --check`

## Follow-Up Options

- Replace mechanize with `requests` plus explicit form handling if this sample is
  maintained beyond compatibility mode.
- Add a `settings.example.py` with target-site placeholders if the owner wants a
  runnable demo configuration.
- Add CI once the repository owner wants verification on every push.
