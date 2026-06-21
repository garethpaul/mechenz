# Spaced Makefile Path

status: completed

## Problem

GNU Make list functions split `MAKEFILE_LIST` on whitespace, so the documented
absolute `make -f` workflow failed when the checkout path contained spaces.

## Change

1. Derive the root from the raw Makefile path with shell-safe quote handling
   and POSIX `printf`/`sed` normalization.
2. Preserve `override ROOT` and reject command-line or environment replacement
   of `MAKEFILE_LIST`.
3. Dry-run verification, cleanup, and formatting gates from an unrelated
   directory against a path containing spaces, brackets, and a literal apostrophe.

## Verification

- Root and external `make lint`, `make test`, `make build`, `make check`,
  `make clean`, and `make fmt` gates passed.
- Hostile `ROOT` values could not redirect commands.
- Command-line and environment `MAKEFILE_LIST` attacks failed closed.
- No SMTP, memcache, scraping target, credential, or live network service was
  used by the path-resolution regression.
