# Close Scrape Responses Deterministically

status: planned

## Context

`fetch_actions` replaces the submitted-form response when `form_url` is set
and reads the selected response without closing it. A bounded read or parser
failure therefore leaks the final response, while the optional result URL path
also leaks the superseded response.

## Requirements

- Close the submitted-form response before replacing it with a result URL
  response.
- Close the selected final response after bounded reading, including read and
  size-limit failures.
- Preserve request timeouts, the total `limit + 1` read budget, short-read
  assembly, exact-limit acceptance, one-byte-over rejection, and parsing
  behavior.
- Add focused regressions for the direct submission path, the result URL path,
  and exceptional bounded reads.
- Extend portable static contracts and maintenance guidance without contacting
  live scrape, cache, or SMTP services.

## Implementation

1. Give the response fake observable close state and allow the browser fake to
   return distinct responses for each network open.
2. Close a submitted response immediately before replacing it with the optional
   result URL response.
3. Wrap bounded reading of the selected response in `try/finally` so every exit
   closes it exactly once.
4. Add mutation-sensitive checker contracts and concise operator guidance.

## Verification

- Run focused response lifecycle tests and the complete offline suite.
- Run every Make gate from the checkout and the canonical check from an
  external directory with explicit timeouts.
- Reject isolated mutations that remove superseded-response closure,
  final-response closure, exceptional-path coverage, plan completion, or
  guidance.
- Audit the exact diff, Python formatting/compilation, generated artifacts,
  credential patterns, conflict markers, binaries, large files, and intended
  paths before commit.

## Risks

- A response must not be closed before its bounded read completes.
- The same response object may be returned by simplistic test doubles; tests
  should model distinct network responses so replacement ownership is clear.
- The stacked base pull request must remain available and merge first.
