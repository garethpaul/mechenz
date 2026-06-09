# Scrape URL Validation

status: completed

## Context

`load_scrape_settings` rejected blank scrape settings but still accepted any
non-empty `site` or `form_url` value. Live scraping should fail before
mechanize opens malformed URLs or non-HTTP(S) targets such as local file paths.

## Objectives

- Validate `site` as an HTTP(S) URL with a host before live scraping.
- Validate non-empty `form_url` values with the same URL guard.
- Report only setting names for invalid scrape URLs, not configured values.
- Extend tests, static baseline, and docs for the scrape URL validation guard.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
