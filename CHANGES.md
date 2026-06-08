# Changes

## 2026-06-08

- Ported the scraper and SMTP helper to Python 3-compatible imports and syntax.
- Added runtime-only imports for optional live dependencies so tests can run without mechanize, memcache, or live SMTP.
- Added environment-backed SMTP configuration with an ignored `settings.py` compatibility fallback.
- Added parser, cache, notification, and SMTP unit tests using the Python standard library.
- Added dependency metadata and `make check` verification.
