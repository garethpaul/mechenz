# Python 3 Scraper Baseline Plan

## Context

`mechenz` is a Python 2-era scraper that submits a form-backed site, parses
`div.action` entries, compares results through memcache, and sends a Gmail SMTP
notification when data changes. The repository did not include the local
`settings.py`, dependency metadata, or tests.

## Risks

- Python 2 imports and `dict.iteritems()` prevent the script from running on a
  supported Python runtime.
- Importing local settings and live dependencies at module import time makes
  tests require secrets, memcache, network access, and SMTP credentials.
- Scraped data and Gmail credentials are sensitive and need explicit ignored
  local configuration.
- Parser/cache/email behavior could regress without fixture-based tests.

## Work Completed

- Ported the scraper and mail helper to Python 3-compatible imports and
  dictionary iteration.
- Replaced the BeautifulSoup dependency for the current parser use case with a
  small `HTMLParser`-based extractor.
- Kept `mechanize` and `python-memcached` as live runtime dependencies in
  `requirements.txt`.
- Added `settings.py.example` and `.gitignore` rules for local secrets and
  Python caches.
- Added unit tests for action parsing, email-body formatting, change detection,
  cache updates, and settings validation.
- Added `make check` for bytecode compilation and unit tests.

## Verification

- `make check`
- `python3 -m unittest discover -s tests`
- `git diff --check`
