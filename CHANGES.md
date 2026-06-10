# Changes

## 2026-06-10

- Added scrape encoding validation so unknown response codecs fail before live
  scraping without echoing raw configuration values.

## 2026-06-09

- Added local `make lint` and `make build` gate targets alongside `make test`
  and `make check` for the Python scraper baseline.
- Added scrape URL validation so malformed or non-HTTP(S) target URLs fail
  before live scraping.
- Added SMTP recipient normalization so blank recipient lists fail before an
  SMTP connection is opened.
- Added SMTP header validation so CRLF in sender, recipient, or subject values
  fails before an SMTP connection is opened.
- Added robot setting validation so ambiguous `respect_robots` or
  `MECHENZ_IGNORE_ROBOTS` values fail closed without echoing raw values.

## 2026-06-08

- Ported the scraper and SMTP helper to Python 3-compatible imports and syntax.
- Added runtime-only imports for optional live dependencies so tests can run without mechanize, memcache, or live SMTP.
- Added environment-backed SMTP configuration with an ignored `settings.py` compatibility fallback.
- Added scrape settings validation for blank live-run target, recipient, user-agent, and referer values.
- Added SMTP numeric setting validation that rejects invalid port and timeout values without echoing raw configuration.
- Added parser, cache, notification, and SMTP unit tests using the Python standard library.
- Added dependency metadata and `make check` verification.
