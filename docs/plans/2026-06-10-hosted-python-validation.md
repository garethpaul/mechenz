# Hosted Python Validation

status: completed

## Context

The repository has dependency metadata, offline scraper and SMTP tests,
compilation checks, and a canonical local gate, but no hosted validation. Local
tests intentionally avoid optional live integrations, so dependency installation
also needs an explicit hosted check.

## Priorities

1. Install and validate the declared Python dependencies on Python 3.12.
2. Run the canonical `make check` gate on hosted Linux.
3. Enforce a pinned, read-only, bounded workflow from the baseline checker.
4. Keep live scraping, memcached access, SMTP authentication, and email delivery
   outside hosted validation.

## Implementation Units

### Workflow And Checker

Files:

- `.github/workflows/check.yml`
- `scripts/check-baseline.py`

Add push, pull-request, and manual triggers; read-only permissions; concurrency
cancellation; a bounded `ubuntu-24.04` job; commit-pinned, credential-free
checkout and Python setup; dependency caching; requirements installation; `pip
check`; and `make check`. Require that contract from the baseline checker.

### Documentation

Files:

- `README.md`
- `VISION.md`
- `SECURITY.md`
- `CHANGES.md`
- `docs/plans/2026-06-10-hosted-python-validation.md`

Document hosted dependency and offline test validation without implying live
scraper, cache, or mail integration coverage.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- workflow YAML parse
- `git diff --check`
- successful hosted Linux `Check` workflow for the pushed commit

## Boundaries

- Do not provide SMTP credentials, a private settings file, or target-site data.
- Do not contact target sites, memcached, or SMTP services in CI.
