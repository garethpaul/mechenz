# CI Baseline

status: completed

## Context

The repository had a local Python `make check` baseline for scraper settings,
SMTP guardrails, unit tests, and module compilation, but no hosted workflow ran
it for pushes and pull requests.

## Changes

- Added a pinned, read-only GitHub Actions workflow that installs Python 3.12,
  disables persisted checkout credentials, installs `requirements.txt`, runs
  `pip check`, and executes `make check`.
- Extended the baseline guard and docs so the hosted CI path stays visible.

## Verification

- `make check`
- hosted GitHub Actions push and pull-request runs
