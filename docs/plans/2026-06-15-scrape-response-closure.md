# Close Scrape Responses Deterministically

status: completed

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

## Work Completed

- Closed the submitted-form response before replacing it with an optional
  result URL response.
- Wrapped the selected response's bounded read in `try/finally` so success,
  size-limit rejection, and read errors release it deterministically.
- Added distinct response fakes plus direct, replacement, and read-failure
  lifecycle assertions.
- Added static contracts and operator, security, and maintenance guidance.

## Verification Completed

- The focused response lifecycle tests and all 37 offline tests passed.
- Python source compilation and `make fmt` passed. All four Make gates passed
  from the checkout, and the canonical check passed from an external directory
  through the absolute Makefile path after an explicit artifact inventory.
- Six isolated hostile mutations were rejected: missing superseded-response
  closure, missing final-response closure, missing exceptional-path coverage,
  missing static ownership contracts, missing guidance, and stale plan status.
- Checker compilation and `git diff --check` passed. Exact intended-path,
  generated-artifact, secret-pattern, conflict-marker, binary, and large-file
  audits found no issues.
- No live target, memcache, SMTP, or other external integration was contacted.
