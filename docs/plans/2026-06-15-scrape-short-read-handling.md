# Scrape Short Read Handling

status: in progress

## Context

The response-size helper performs one bounded `read(limit + 1)`. File-like
network responses may legally return fewer bytes than requested before EOF, so
one short read can silently truncate the HTML and leave later bytes unmeasured.

## Requirements

- Continue reading after nonempty short reads until EOF or the total
  `limit + 1` budget is exhausted.
- Never request or retain more than one byte beyond the configured limit.
- Preserve exact-limit acceptance and one-byte-over rejection.
- Add an advancing response fake and regression tests for short-read assembly
  and oversized data split across chunks.
- Extend static contracts and maintenance guidance without changing requests,
  parsing, cache, email, or dependency behavior.

## Implementation

1. Give the response fake a cursor and optional maximum chunk size.
2. Accumulate response chunks while decrementing one fixed total read budget.
3. Reject the joined body when its size exceeds the existing maximum.
4. Add focused tests, ordering-sensitive checker contracts, and guidance.

## Verification

- Run focused response-reader tests, the full offline suite, `make fmt`, every
  Make gate, and the rooted canonical check from an external directory.
- Verify isolated mutations to loop continuation, remaining-budget accounting,
  EOF handling, split oversize rejection, plan status, and guidance are rejected.
- Run checker compilation plus exact diff, generated-artifact, secret-pattern,
  conflict-marker, binary, large-file, and intended-path audits.

## Risks

- A broken stream that never returns bytes must terminate immediately on its
  empty read rather than spin.
- The total retained body must remain capped at `limit + 1` across all chunks.
- The stacked base pull request must remain available and merge first.

## Work Completed

- Pending implementation.

## Verification Completed

- Pending validation.
