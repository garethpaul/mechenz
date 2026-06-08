---
title: Issue 1 Settings Loader
type: fix
status: active
date: 2026-06-08
origin: https://github.com/garethpaul/mechenz/issues/1
execution: code
---

# Issue 1 Settings Loader

## Summary

Add a tracked, secret-free `settings.py` so clean checkouts fail with clear
configuration guidance instead of `ImportError`.

## Problem Frame

Issue #1 was filed because `main.py` and `RoyalMail.py` import `settings`, but
the repository does not include that module or a template. Developers cannot
run or inspect startup behavior from a clean checkout without guessing the
required settings.

## Requirements

- R1. Track a safe `settings.py` module.
- R2. Read credentials, URLs, and form values from environment variables.
- R3. Keep SMTP credentials and site-specific form values out of git.
- R4. Raise a clear error naming the missing setting.
- R5. The PR must reference `https://github.com/garethpaul/mechenz/issues/1`.

## Implementation Unit

### U1. Environment Settings Loader

- **Goal:** Add `settings.py`, document the required `MECHENZ_*` variables, and
  add focused tests for missing, valid, and invalid form configuration.
- **Files:** `settings.py`, `settings_tests.py`, `README.md`,
  `scripts/check-baseline.sh`
- **Test Scenarios:** Missing config names the missing env var, full config
  loads all names used by the app, `form` still supports `.iteritems()`, and
  invalid form JSON fails clearly.
- **Verification:** `python3 settings_tests.py`, `python3 -m py_compile
  settings.py settings_tests.py main.py RoyalMail.py`,
  `scripts/check-baseline.sh`, and `git diff --check`.
