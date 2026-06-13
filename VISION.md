## Mechenz Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

Mechenz is a Python scraper and email notification script. It uses mechanize,
memcache, and SMTP to detect changed scraped data and send a notification email.

The repository is useful as a small automation sample for polling a form-backed
site, caching previous results, and notifying via email.

The goal is to keep the automation understandable while making credentials,
scraping behavior, and email delivery safe.

Current baseline: `make lint`, `make test`, `make build`, and `make check`
cover the static baseline, offline unit tests, Python compilation, generated
artifact cleanup, action parsing, email body generation, cache comparison,
settings validation, scrape settings validation, notification delivery, SMTP
environment configuration, SMTP numeric setting validation, and SMTP TLS/login
setup, SMTP header validation, and nested action parser depth.

The current focus is:

Priority:

- Preserve the scrape, cache, compare, and email-notification flow
- Keep site/form settings and SMTP credentials out of git
- Keep scrape settings validation strict enough to reject blank live-run targets
- Keep scrape URL validation strict enough to reject non-HTTP(S) live-run targets
- Keep scrape encoding validation strict enough to reject unknown response codecs
- Keep nested action parser depth balanced across ordinary inner containers
- Keep SMTP ports within `1..65535`, SMTP timeouts finite and at most 300
  seconds, and validation errors free of raw configuration values
- Keep SMTP recipient normalization before opening outbound SMTP connections
- Keep SMTP header validation before opening outbound SMTP connections
- Keep robot setting validation strict enough that typos fail closed
- Avoid ignoring robots or site terms without explicit documentation
- Keep offline tests independent of live scraping, memcache, Gmail, and local credentials
- Keep `make lint`, `make test`, `make build`, and `make check` available as
  local verification gates
- Keep pinned, read-only, credential-free Python 3.12 hosted validation
  covering dependency installation, `pip check`, and offline tests without
  live integrations
- Maintain security policy for the sample

Next priorities:

- Add fixture-driven tests for additional distinct target response shapes
- Add rate-limit and target-site access notes before changing scrape behavior

Contribution rules:

- One PR = one focused scraper, cache, mail, or documentation change.
- Do not commit Gmail credentials, target-site secrets, or scraped private data.
- Run `make lint`, `make test`, `make build`, and `make check` before pushing changes.
- Verify behavior with fixtures before live scraping.
- Document target-site access assumptions.
- Preserve scrape settings validation when changing live-run configuration.

## Security And Privacy

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Email credentials and scraped data are sensitive. Credentials must stay in local
configuration, and scraped content should not be committed unless it is safe as
a fixture.

## What We Will Not Merge (For Now)

- SMTP passwords or account credentials
- Scraped private data
- Live-only tests as the default path
- Scraping changes without access and rate-limit notes

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
