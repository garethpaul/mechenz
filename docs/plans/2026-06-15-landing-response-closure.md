---
title: Landing Response Closure
type: reliability
status: completed
date: 2026-06-15
execution: code
---

# Landing Response Closure

## Problem

`fetch_actions` discards the initial landing-page response returned by
`browser.open(settings.site)`. The response is never explicitly closed, and a
form-selection or form-population failure can leave its network resources open.

## Approach

- Retain the landing response while selecting and populating the form.
- Close it in a `finally` block before opening the submitted request, including
  selection, population, and click failures.
- Preserve submitted/replacement response ownership, request timeouts, bounded
  reads, parsing, and settings behavior.
- Add success and exceptional-path lifecycle regressions plus static contracts,
  maintained guidance, and completed plan evidence.

## Files

- `main.py`
- `tests/test_main.py`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-15-landing-response-closure.md`

## Verification

- Prove the landing response remains open against the previous implementation.
- Run focused lifecycle tests and all repository/external Make gates.
- Reject isolated ownership, ordering, exceptional-path, guidance, and plan
  mutations.
- Audit the exact diff, generated artifacts, and secret patterns.

## Non-Goals

- Do not change target sites, form data, parsing, cache, SMTP, or retry policy.
- Do not contact live target, memcache, or mail services.
- Do not merge or close stacked pull requests without owner authorization.

## Status: Completed

## Work Completed

- Retained the landing response through form preparation and closed it in a
  `finally` block before the submitted request is opened.
- Added success and form-selection failure regressions proving exactly one
  landing-response close and no submitted open after preparation failure.
- Added ownership, ordering, regression, guidance, and completed-plan contracts.

## Verification Completed

- Focused regressions failed against the previous implementation and passed
  after deterministic landing-response ownership was added.
- All 38 offline tests passed through the focused suite and every Make gate.
- Repository and absolute-Makefile checks passed from an external directory.
- Six isolated hostile mutations were rejected for ownership, close ordering,
  success coverage, exceptional-path coverage, guidance, and plan status.
- Exact diff, generated-artifact, conflict-marker, and secret-pattern audits passed.
- No live target, memcache, or SMTP integration was contacted.
