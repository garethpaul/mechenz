# Bounded Scrape Response

status: completed

## Context

The final mechanize response is read without a byte limit before HTML parsing.
An unexpectedly large target response can therefore amplify memory and parser
work, and the response is not deterministically closed by the application.

Mechanize may buffer transport data before the application reads it, so this
change bounds content entering the parser rather than claiming to cap all
network memory.

## Priorities

1. Read at most 1 MiB plus one overflow byte from the final response.
2. Reject oversized bodies before decoding or HTML parsing.
3. Close final and superseded submit responses deterministically.
4. Cover the behavior with injected, offline browser/response fakes.

## Implementation Units

### Response Boundary

File: `main.py`

Add a focused response reader that performs a one-byte overflow probe, raises a
generic size error without including response content, and closes the response
in all paths. Close the submit response before following an explicit form URL.

### Offline Tests

File: `tests/test_main.py`

Add fakes that assert the exact read size, successful action extraction,
oversized rejection before parsing, and deterministic response closure for both
the submit and final form-URL responses.

### Static Contract And Documentation

Files:

- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-12-bounded-scrape-response.md`

Document the parser-input boundary and its transport-buffering limitation.

## Verification

Completed locally on 2026-06-12:

- `python3 -m py_compile main.py tests/test_main.py scripts/check-baseline.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_main.py'` (14 tests)
- `make lint`
- `make test` (26 tests)
- `make build`
- `make check` (26 tests plus static and build checks)
- hostile mutations: removing the overflow-byte probe failed two focused tests;
  removing guaranteed response closure failed three focused tests
- `git diff --check`

Hosted push and pull-request checks will be recorded after the branch is pushed.

## Boundaries

- Do not make live scrape requests in tests or CI.
- Do not include response content in the size error.
- Do not claim to stop mechanize or lower layers from buffering network data.
