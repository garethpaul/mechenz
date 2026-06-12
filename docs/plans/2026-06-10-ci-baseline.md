# CI Baseline

status: completed

## Context

The repository had a local Python `make check` baseline for scraper settings,
SMTP guardrails, unit tests, and module compilation, but no hosted workflow ran
it for pushes and pull requests.

## Changes

- Added a GitHub Actions workflow that installs Python 3.12 and runs
  `make check`.
- Extended the baseline guard and docs so the hosted CI path stays visible.

## Verification

- `make check`
