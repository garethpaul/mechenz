# Scrape Encoding Validation

status: completed

## Context

`load_scrape_settings` accepts an optional response encoding for decoding live
scrape responses. Unknown codec names should fail during configuration
validation rather than later inside response parsing.

## Completed Scope

- Added a codec lookup guard for configured scrape encodings.
- Preserved blank encoding fallback to `utf-8`.
- Returned a stable `invalid encoding` error without echoing raw configuration
  values.
- Added offline unit coverage and extended the static baseline/docs.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
