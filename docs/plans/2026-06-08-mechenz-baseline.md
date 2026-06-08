# Mechenz Baseline Plan

status: completed

## Context

`mechenz` is a Python scraper and email notification sample. It polls a
form-backed page, extracts action text, stores the latest result in memcache,
and sends a Gmail SMTP notification when the scraped data changes.

## Risks

- Importing modules required a private `settings.py` and live third-party
  packages, which made offline verification difficult.
- SMTP credentials, target site settings, and scraped data are sensitive and
  should stay in local configuration.
- The email body and cache comparison behavior had no tests.

## Work Completed

- Added runtime dependency loading so pure helpers can be imported without
  mechanize, memcache, Gmail, live scraping, or private settings.
- Added injectable cache, settings, date, mailer, and SMTP seams.
- Added SMTP environment configuration with ignored local-settings fallback.
- Set the live scraper to respect robots unless explicitly overridden.
- Updated cache state only after successful email delivery so send failures can
  be retried.
- Added unit tests for change detection, email body formatting, notification
  delivery arguments, SMTP environment configuration, and SMTP TLS/login flow.
- Added `settings.py.example`, `requirements.txt`, `.gitignore`, and
  `make check`.

## Verification

- `make check`
- `python3 -m unittest discover -s tests`
- `git diff --check`
