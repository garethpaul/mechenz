# Scrape Settings Validation Plan

status: completed

## Context

`load_scrape_settings` validates that the local settings module defines the
scraper fields needed for a live run. It trimmed values before returning them,
but blank required values such as job name, recipient, target site, user agent,
or referer could still pass validation and fail later in scraping, caching, or
email delivery.

## Objectives

- Preserve the existing required settings list.
- Reject blank required scrape settings after trimming.
- Keep `form_url` available as an optional follow-up URL for sites where the
  submitted response already contains the action list.
- Cover blank settings validation with offline unit tests.
- Extend the static baseline so future changes keep scrape settings validation
  visible.

## Verification

- `make check`
- `python3 -m unittest discover -s tests`
- `python3 scripts/check-baseline.py`
- `git diff --check`
