# SMTP Header Validation

status: completed

## Context

Mechenz sends notification email with sender, recipient, and subject values
derived from local settings and runtime flow. Recipient normalization rejected
blank addresses, but CRLF in header values could still reach MIME header
construction.

## Completed Scope

- Added SMTP header validation for sender login, recipients, and subject.
- Rejected CRLF values before opening an SMTP connection.
- Added offline tests for invalid sender, recipient, and subject values.
- Extended the static baseline and docs to preserve the guardrail.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
