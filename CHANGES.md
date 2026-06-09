# Changes

## 2026-06-09

- Added scrape URL validation so malformed or non-HTTP(S) target URLs fail
  before live scraping.
- Added SMTP recipient normalization so blank recipient lists fail before an
  SMTP connection is opened.

## 2026-06-08

- Ported the scraper and SMTP helper to Python 3-compatible imports and syntax.
- Added runtime-only imports for optional live dependencies so tests can run without mechanize, memcache, or live SMTP.
- Added environment-backed SMTP configuration with an ignored `settings.py` compatibility fallback.
- Added scrape settings validation for blank live-run target, recipient, user-agent, and referer values.
- Added SMTP numeric setting validation that rejects invalid port and timeout values without echoing raw configuration.
- Added parser, cache, notification, and SMTP unit tests using the Python standard library.
- Added dependency metadata and `make check` verification.
