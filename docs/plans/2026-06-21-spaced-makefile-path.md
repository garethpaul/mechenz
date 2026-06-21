# Spaced Makefile Path

status: completed

## Problem

GNU Make list functions split `MAKEFILE_LIST` on whitespace, so the documented
absolute `make -f` workflow failed when the checkout path contained spaces.

## Change

1. Derive the root from the final existing trusted Makefile suffix with Python
   `shlex` quoting, so inert earlier `-f` files do not poison either absolute
   or relative repository Makefile invocations.
2. Freeze the derived `ROOT` for every checked-in gate target so a later
   duplicate global `override ROOT` cannot redirect `make check` before the real
   policy executes.
3. Reject command-line or environment replacement of `MAKEFILE_LIST`, reject
   `MAKEFILES` preloads, and force the recipe `SHELL` back to `/bin/sh`.
4. Treat arbitrary extra makefiles as caller-supplied code. The Makefile keeps
   inert extra `-f` paths from corrupting root derivation, but does not sandbox
   code a caller asks GNU Make to read.

## Verification

- Root and external `make lint`, `make test`, `make build`, `make check`,
  `make clean`, and `make fmt` gates passed from a checkout path containing
  spaces, brackets, and a literal apostrophe.
- A real `make check` probe with a later duplicate `override ROOT` executed the
  real checkout's static check, unit test, mutation test, and compile recipes,
  not the fake root's recipes.
- Hostile `ROOT` values could not redirect commands, and command-line and
  environment `MAKEFILE_LIST` attacks failed closed.
- `MAKEFILES` preload attacks failed closed, caller `SHELL` overrides did not
  replace the recipe shell, and an inert earlier `-f` file did not poison root
  derivation for absolute or relative trusted Makefile paths.
- No SMTP, memcache, scraping target, credential, or live network service was
  used by the path-resolution regression.
