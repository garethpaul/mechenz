# Make Gate Targets

status: completed

## Context

The repository already had `make check`, `make test`, `compile`, and
`static-check` targets, but the shared maintenance workflow expects `make lint`,
`make test`, `make build`, and `make check` to be available before a change is
pushed.

## Completed Scope

- Added `make lint` as the static baseline entry point.
- Added `make build` as the Python compilation entry point.
- Kept `make test` for offline unit tests.
- Kept `make check` as the full gate by chaining clean, lint, test, and build.
- Updated README, VISION, CHANGES, and the static baseline so the gate contract
  is visible and enforced.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
