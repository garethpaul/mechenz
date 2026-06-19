---
title: "fix: Bound memcache socket operations"
type: fix
status: completed
date: 2026-06-17
execution: code
---

# Bound Memcache Socket Operations

## Summary

Add a finite, validated socket timeout to the optional `python-memcached`
client so an unavailable or unresponsive cache cannot stall the scraper and
notification process indefinitely. Preserve the existing cache server
selection and offline test strategy.

## Problem Frame

The scraper and SMTP integrations already use explicit timeouts, but
`create_cache` constructs `memcache.Client` without `socket_timeout`. The
pinned `python-memcached` 1.62 client supports a timeout applied to every cache
socket call; leaving it unset delegates to the process-wide socket default,
which can be unbounded. A stalled cache lookup or update can therefore prevent
scraping, notification delivery, or normal process completion.

## Requirements

- R1. Every production memcache client receives an explicit finite socket
  timeout.
- R2. The default timeout is 5 seconds when no environment or settings value is
  configured.
- R3. A nonblank `MEMCACHE_TIMEOUT` environment value takes precedence over a
  `memcache_timeout` settings value.
- R4. Timeout values must be numeric, finite, greater than zero, and no greater
  than 300 seconds; validation errors must not echo raw configuration values.
- R5. Existing memcache server normalization and lazy client import behavior
  remain unchanged.
- R6. Tests and the static baseline must reject removal, bypass, or weakening of
  the timeout boundary without contacting a live memcache service.

## Key Technical Decisions

- KTD1. Reuse a small local float parser in `main.py` rather than importing the
  SMTP module's private parser. The cache configuration belongs to the scraper
  module and should not couple cache construction to mail internals.
- KTD2. Use the pinned client's `socket_timeout` constructor argument. This is
  the library's direct boundary for connection and subsequent socket calls and
  avoids process-global `socket.setdefaulttimeout` side effects.
- KTD3. Keep one timeout value for all configured cache servers. This matches
  the selected client's API and keeps the compatibility change narrow.

## Scope Boundaries

- Do not replace `python-memcached`, change cache keys, or alter change
  notification semantics.
- Do not add retries, fallback storage, or swallow cache failures.
- Do not resolve hosts or connect to memcache in tests.
- Do not merge or close any stacked pull request without explicit owner
  authorization.

## Implementation Units

### U1. Validate cache timeout configuration

- **Goal:** Resolve a bounded timeout before importing or constructing the
  optional memcache client.
- **Files:** `main.py`, `settings.py.example`
- **Requirements:** R1, R2, R3, R4, R5
- **Test scenarios:** Default value, settings value, environment override,
  blank environment fallback, zero, negative, nonnumeric, infinite, NaN, and
  values above the maximum.

### U2. Protect behavior with runtime and static contracts

- **Goal:** Prove exact timeout propagation and make regressions mutation
  sensitive without requiring the dependency or a live server.
- **Files:** `tests/test_main.py`, `scripts/check-baseline.py`
- **Requirements:** R1, R3, R4, R5, R6
- **Test scenarios:** Injected fake client receives `socket_timeout`; invalid
  values fail before client import; hostile changes to defaults, precedence,
  validation, propagation, or test contracts are rejected.

### U3. Record the operational boundary

- **Goal:** Keep maintainer guidance and completed evidence aligned with the
  implementation.
- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`,
  `docs/plans/2026-06-17-memcache-socket-timeout.md`
- **Requirements:** R1, R2, R4, R6
- **Verification:** Guidance names the default, configuration source, allowed
  range, and the fact that timeout handling does not prove cache availability.

## Risks and Dependencies

- A timeout limits waiting but does not make memcache available; failures still
  propagate according to the existing client behavior.
- Very small configured values can make slow but healthy cache operations fail,
  so the plan allows explicit configuration while enforcing a positive upper
  bound.
- `python-memcached` is maintenance-mode software. Replacing it is a separate
  dependency migration with broader behavior and serialization implications.

## Acceptance Examples

- AE1. With no timeout configuration, a fake memcache client receives
  `socket_timeout=5.0`.
- AE2. With `memcache_timeout="12.5"`, the client receives `12.5`.
- AE3. With settings `12.5` and environment `MEMCACHE_TIMEOUT="2"`, the client
  receives `2.0`.
- AE4. With blank environment configuration, the settings value remains
  authoritative.
- AE5. Values such as `0`, `-1`, `nan`, `inf`, `301`, or `not-a-number` raise a
  sanitized `ValueError` before the optional memcache module is imported.

## Verification Plan

- Run focused cache-construction tests, then the complete offline suite and all
  canonical Make gates.
- Run the absolute Makefile check from an external directory.
- Run isolated hostile mutations for timeout propagation, default value,
  precedence, finite/range validation, focused tests, guidance, and plan
  completion evidence.
- Audit the exact diff, generated artifacts, credential patterns, conflict
  markers, and intended paths before committing.

## Sources and Research

- `python-memcached` 1.62 source defines `Client(..., socket_timeout=...)`,
  stores the value on each server object, and applies it with
  `socket.settimeout` before network operations:
  <https://github.com/linsomniac/python-memcached/blob/1.62/memcache.py>
- The pinned package remains `python-memcached==1.62` in `constraints.txt`, so
  this plan targets the repository's reviewed dependency resolution rather than
  an unverified newer API.

## Work Completed

- Added the 5-second default and bounded `MEMCACHE_TIMEOUT` or
  `memcache_timeout` configuration with sanitized invalid-value errors.
- Passed the validated value to the pinned client's `socket_timeout` argument
  before any optional memcache import or construction.
- Added runtime coverage for default, settings, environment precedence, blank
  environment fallback, propagation, finite/range rejection, pre-import
  validation, and error sanitization.
- Added mutation-sensitive static contracts, settings-template guidance, and
  maintained operational documentation.

## Verification Completed

- All 41 offline tests passed, including 28 focused scraper/cache tests.
- Repository formatting, test, compilation, lint, build, and check gates passed;
  the absolute Makefile check also passed from an external directory.
- Eight isolated hostile mutations were rejected for the default, client
  propagation, environment precedence, finite validation, upper bound, focused
  test, guidance, and plan completion status.
- Exact diff, artifact, conflict-marker, intended-path, and credential-pattern
  audits passed with no findings.
- No live memcache server was contacted.
