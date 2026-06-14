# Scrape Response Body Limit

status: planned

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

Pending implementation.

## Verification Completed

Pending validation.
