# Memcache Server Normalization

Status: planned

## Problem

`create_cache` converts `settings.memcache_servers` with `list()`. A single
string therefore becomes one server entry per character, while blank endpoints
inside configured sequences reach the memcache client unchanged. These
configuration errors fail later and less clearly than the maintained settings
validation boundary.

## Scope

- Accept a single nonblank server string or a sequence of nonblank server
  values from `settings.memcache_servers`.
- Let a nonblank `MEMCACHE_SERVER` environment value override the configured
  list after whitespace normalization.
- Reject empty or malformed server collections before constructing the client.
- Preserve the default localhost endpoint and do not connect to memcache in
  tests.

## Implementation

1. Add a focused server-normalization helper in `main.py` and use it from
   `create_cache`.
2. Add unit coverage for string, sequence, environment override, blank-entry,
   and unsupported-type behavior in `tests/test_main.py`.
3. Extend `scripts/check-baseline.py` and maintenance guidance to protect the
   validation contract and completed evidence.

## Validation

- Run the focused main tests and all canonical Make gates from the checkout and
  an external directory.
- Verify mutations that restore character splitting, retain blank endpoints,
  bypass environment normalization, or leave this plan incomplete are rejected.
- Run dependency, diff, artifact, conflict-marker, intended-path, and
  secret-pattern audits.

## Risks

- This validates configuration shape and nonblank values only; it does not
  resolve hosts, open sockets, or prove memcache availability.
- The stacked base PR must remain available and merge before this change.
