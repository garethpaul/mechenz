# SMTP Numeric Bounds

status: completed

## Problem

SMTP port and timeout settings reject non-numeric and non-positive values, but
still accept ports outside the TCP range and non-finite or excessively long
timeouts. Those values defer configuration failure to the network layer and can
leave notification attempts effectively unbounded.

## Scope

- Restrict `SMTP_PORT` to the valid `1..65535` range.
- Require a finite `SMTP_TIMEOUT` no greater than 300 seconds.
- Preserve sanitized validation errors that do not echo configuration values.
- Add offline boundary tests and static mutation guardrails.
- Document the runtime limits without changing SMTP credentials or delivery.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- mutation checks for the port and timeout upper bounds
- `git diff --check`

## Work Completed

- Declared the SMTP port maximum as 65535 at the configuration call site.
- Declared a 300-second SMTP timeout maximum and rejected non-finite floats.
- Added offline tests for zero and oversized ports plus NaN, infinity, and
  oversized timeout values.
- Extended the static baseline with mutation-sensitive source, test, plan, and
  documentation assertions.
- Documented both runtime bounds in project and security guidance.
