# Changes

## 2026-06-13

- Made tests, compilation, static checks, formatting checks, and generated-file
  cleanup resolve from the checkout for absolute Makefile invocations.
- Corrected nested action parser depth so ordinary inner containers cannot
  end an action before its first span is read.

## 2026-06-12

- Stopped the hosted checkout from persisting its credential and added an exact
  static contract for the sole workflow, permissions, and checkout step.

## 2026-06-10

- Added a reviewed five-package Python 3.12 constraints graph for hosted
  dependency resolution, with exact workflow, cache, documentation, and plan
  contracts. Version constraints do not authenticate package artifacts.
- Bounded SMTP ports to `1..65535` and SMTP timeouts to finite values no
  greater than 300 seconds.
- Added pinned, read-only Python 3.12 hosted validation for dependency
  installation, `pip check`, and the offline canonical gate.
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
