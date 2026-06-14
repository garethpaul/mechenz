# Scrape Response Body Limit

status: completed

## Context

Every mechanize network open has a finite timeout, but the selected response is
still consumed with an unbounded `read()`. A target can return a very large body
within that timeout and cause avoidable memory pressure before parsing begins.

## Requirements

- Read at most one byte beyond a fixed response-body limit.
- Reject oversized responses before HTML decoding or action parsing.
- Preserve headers, robots handling, form submission, optional result-page
  selection, configured response encoding, and offline execution.
- Add boundary-sensitive offline tests, static contracts, and maintenance
  guidance.
- Do not add live target requests, change dependency pins, or alter cache and
  email behavior.

## Implementation

1. Add one explicit maximum response-body byte constant and a helper that reads
   with `limit + 1`, rejects an oversized result, and returns accepted bytes.
2. Route the final selected response through that helper before
   `extract_actions`.
3. Extend `tests/test_main.py` for exact-limit acceptance, one-byte-over
   rejection, and the bounded read request.
4. Extend `scripts/check-baseline.py`, `README.md`, `SECURITY.md`, `VISION.md`,
   and `CHANGES.md` with mutation-sensitive contracts and guidance.

## Verification

- Run focused and full offline tests, every Make gate, and the rooted canonical
  check from an external directory.
- Verify isolated mutations to the limit, read size, comparison, parser
  ordering, boundary tests, plan status, and maintenance guidance are rejected.
- Run checker compilation plus exact diff, generated-artifact, secret-pattern,
  conflict-marker, binary, large-file, and intended-path audits.

## Risks

- The selected limit must be high enough for the expected action page while
  remaining meaningfully bounded.
- A response exactly at the limit must remain accepted; only larger bodies
  should fail.
- The stacked base PR must remain available and merge before this change.

## Work Completed

- Added a 1 MiB maximum and a bounded response reader that requests one extra
  byte, accepts the exact boundary, and rejects larger bodies.
- Routed the final selected response through the bounded reader before decoding
  and action parsing without changing request, cache, or email behavior.
- Added offline boundary tests, static contracts, and operator/security
  guidance.

## Verification Completed

- The focused response-limit tests and all 34 offline tests passed.
- All four Make gates passed from the checkout with the broad cleanup target
  explicitly treated as already complete, `make fmt` passed, and the same
  non-destructive canonical check passed from an external directory through
  the absolute Makefile path.
- Seven isolated hostile mutations were rejected for the limit constant, read
  size, comparison, parser ordering, boundary tests, plan status, and
  maintenance guidance.
- Checker compilation, constraints consistency, `git diff --check`, and exact
  intended-path, secret-pattern, conflict-marker, generated-artifact, binary,
  and large-file audits passed.
- No live target, memcache, SMTP, or other external integration was contacted.
