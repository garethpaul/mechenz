# Checkout Credential Boundary

status: completed

## Context

The recorded remediation evidence describes checkout credential persistence as
disabled, but the exact Python 3.12 workflow head still uses the checkout
action's default credential behavior. The job only needs repository contents to
install the constrained dependency graph and run offline verification.

## Objectives

- Disable checkout credential persistence without changing dependency or test
  coverage.
- Enforce one workflow, one read-only permission block, one checkout action,
  and one correctly nested non-persisted credential declaration.
- Preserve the Python 3.12 runner, immutable action pins, exact constraints,
  pip cache inputs, bounded execution, and `make check` gate.
- Correct documentation so it matches the exact workflow state.

## Implementation Units

### Workflow And Checker

Files:

- `.github/workflows/check.yml`
- `scripts/check-baseline.py`

Add `persist-credentials: false` beneath the sole checkout action. Extend the
dependency-free checker to reject duplicate workflows, alternate checkout
steps, write scopes, misplaced or contradictory credential declarations, and
incomplete plan evidence.

### Documentation

Files:

- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-12-checkout-credential-boundary.md`

Document the shorter checkout credential lifetime without changing scraper,
SMTP, dependency, or compatibility claims.

## Work Completed

- Added `persist-credentials: false` beneath the sole pinned checkout step.
- Added exact workflow, permission, checkout-action, and credential-declaration
  contracts to the dependency-free checker.
- Rejected alternate checkout steps, write scopes, misplaced or contradictory
  credential settings, and incomplete plan evidence.
- Updated repository documentation without changing runtime or dependency
  contracts.

## Verification Completed

- `python3 -m py_compile scripts/check-baseline.py`
- `python3 scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- workflow YAML parse
- `git diff --check`
- Hostile workflow and plan mutations

All local checks remain offline. Canonical hosted push and pull-request checks
are still required at the exact successor head before owner merge.

## Boundaries

- Do not change application code, tests, requirements, constraints, or sample
  configuration.
- Do not perform live scraping, SMTP delivery, or external service calls.
- Preserve the existing remediation PR and exact dependency evidence.
