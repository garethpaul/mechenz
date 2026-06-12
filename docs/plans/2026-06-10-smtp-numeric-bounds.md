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

## Verification Completed

- Local `make check`, `make lint`, `make test`, and `make build` passed,
  including 23 offline unit tests and Python source compilation.
- `python3 -m py_compile scripts/check-baseline.py` and `git diff --check`
  passed.
- Hostile mutations changing the plan status, inserting an unfinished-work
  marker, falsifying a run ID, removing the SMTP port ceiling, or removing the
  finite timeout check were rejected.
- The main-branch push Check run `27287526596` completed successfully for
  commit `d4555441451142239ee680c722adddd9d98f7f0a`.
- The CodeQL setup run `27402325084` completed successfully for commit
  `d4555441451142239ee680c722adddd9d98f7f0a`.
- SMTP parsing preserves `maximum=65535`, `maximum=300.0`, and
  `math.isfinite(parsed)`, with
  `test_load_mail_settings_rejects_port_outside_tcp_range` and
  `test_load_mail_settings_rejects_unbounded_timeout` covering the boundaries.

## Work Completed

- Declared the SMTP port maximum as 65535 at the configuration call site.
- Declared a 300-second SMTP timeout maximum and rejected non-finite floats.
- Added offline tests for zero and oversized ports plus NaN, infinity, and
  oversized timeout values.
- Extended the static baseline with mutation-sensitive source, test, plan, and
  documentation assertions.
- Documented both runtime bounds in project and security guidance.
