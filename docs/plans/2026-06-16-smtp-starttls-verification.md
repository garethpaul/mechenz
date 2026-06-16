---
title: SMTP STARTTLS Certificate Verification
type: security
status: completed
date: 2026-06-16
execution: code
---

# SMTP STARTTLS Certificate Verification

## Priority

P1 security hardening. Mechenz sends SMTP credentials immediately after
STARTTLS, so the client must explicitly use a certificate-verifying TLS context
before authentication.

## Problem

`RoyalMail.send_mail` calls `SMTP.starttls()` without an explicit `SSLContext`.
Python's SSL guidance recommends `ssl.create_default_context()` for client
connections because it loads trusted certificate authorities, enables
certificate validation and hostname checking, and applies secure protocol and
cipher defaults. The notification path should make that security boundary
explicit and regression-tested rather than depend on compatibility defaults.

## Approach

- Create one default client TLS context immediately before the SMTP session.
- Pass that exact context to `SMTP.starttls(context=...)` before login or mail
  submission.
- Allow the context factory to be injected for deterministic offline tests
  without weakening the production default.
- Add mutation-sensitive runtime and static contracts that fail if the context
  is omitted, replaced, or created after authentication begins.
- Document the verified STARTTLS boundary in maintained project guidance.

## Files

- `RoyalMail.py`
- `tests/test_royal_mail.py`
- `tests/test_royalmail.py`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-16-smtp-starttls-verification.md`

## Verification

- Prove the focused TLS-context test fails against the previous implementation.
- Run the complete offline test suite and all repository Make gates.
- Run the absolute-Makefile check from an external directory.
- Reject isolated mutations that remove context creation, omit the STARTTLS
  context argument, substitute a different context, weaken tests or guidance,
  or leave the plan status incomplete.
- Audit the exact diff, generated artifacts, and credential patterns.

## Scope Boundaries

- Preserve STARTTLS on the configured SMTP host and port; do not switch to
  implicit TLS or change authentication behavior.
- Do not add custom certificate authorities, disable hostname verification, or
  expose a configuration escape hatch for insecure TLS.
- Do not contact a live SMTP service or use production credentials.
- Do not merge or close stacked pull requests without owner authorization.

## References

- Python `ssl` security guidance recommends `ssl.create_default_context()` for
  client use and demonstrates passing it to `SMTP.starttls`.
- Python `smtplib` documents the optional `context` argument as the supported
  TLS configuration boundary for STARTTLS.

## Status: Completed

## Work Completed

- Created one `ssl.create_default_context()` result before opening the SMTP
  session and passed that exact object to `SMTP.starttls(context=...)` before
  authentication.
- Added focused runtime coverage for context-factory invocation, exact context
  identity, STARTTLS-before-login ordering, and the default context's hostname
  and certificate verification properties.
- Added static implementation, test, guidance, and completed-plan contracts.
- Updated maintained project guidance and the changelog with the verified
  STARTTLS boundary.

## Verification Completed

- The focused TLS-context regression failed against the previous implementation
  and passed after the explicit default context was applied.
- All 39 offline tests passed through `make fmt`, `make lint`, `make test`,
  `make build`, and `make check`.
- All five repository Make gates passed, and the absolute-Makefile `make check`
  passed from an external directory.
- Seven isolated hostile mutations were rejected for the SSL import, secure
  context factory, STARTTLS context argument, exact context identity, focused
  test contract, maintained guidance, and completed plan status.
- `git diff --check`, generated-artifact inspection, and intended-diff
  credential-pattern inspection passed with no findings.
- No live SMTP service was contacted and no credential was used.
