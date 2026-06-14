# Scrape Request Timeout

status: completed

## Context

The scraper bounds SMTP operations but leaves mechanize requests on the socket
default. The pinned mechanize 0.4.10 `Browser.open` accepts a timeout, while its
`submit` helper performs an unbounded internal open.

## Requirements

- Apply one finite timeout to the initial page, form submission, and optional
  result-page request.
- Preserve robots, headers, form values, parsing, and offline execution.
- Submit through the clicked request so the network open receives the timeout.
- Add mutation-sensitive offline tests and documentation.

## Verification

- Run focused and full tests, all Make gates, external-directory validation,
  hostile mutations, and exact diff/secret/artifact audits.

## Work Completed

- Added one 15-second timeout constant for every mechanize network open.
- Replaced the unbounded `browser.submit()` helper with `browser.click()` plus
  a bounded `browser.open()` call supported by pinned mechanize 0.4.10.
- Preserved headers, robot handling, form selection and values, result parsing,
  and both optional result-page modes.
- Added offline fake-browser coverage, static contracts, and operator/security
  documentation.

## Verification Completed

- The pinned mechanize 0.4.10 wheel source confirmed that `Browser.open`
  accepts `timeout` and that `Browser.submit()` internally calls `open()`
  without forwarding one.
- The 15 focused parser/scraper tests and all 27 offline tests passed.
- `make lint`, `make test`, `make build`, `make check`, and `make fmt` passed
  from the checkout; the absolute-Makefile `check` gate passed from `/tmp`.
- Seven isolated hostile mutations were rejected for the timeout constant,
  each of the three bounded opens, no-result-page coverage, preserved browser
  configuration, and completed plan evidence.
- Checker compilation, constraints consistency, `git diff --check`, and exact
  secret, conflict-marker, generated-artifact, binary, large-file, and
  unrelated-path audits passed.
