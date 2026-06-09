# Robot Setting Validation

status: completed

## Context

`respect_robots` and `MECHENZ_IGNORE_ROBOTS` decide whether the live scraper asks
mechanize to honor robot handling. The old truthy parser treated unknown strings
as false, so a typo could silently disable robot handling or ignore an intended
override.

## Objectives

- Parse documented true and false boolean values for robot settings.
- Reject ambiguous robot setting values by field name.
- Avoid echoing raw invalid configuration values in errors.
- Preserve the documented explicit ignore-robots override.
- Extend tests, static checks, and docs so robot setting validation remains
  visible.

## Verification

- `make check`
- `python3 -m unittest discover -s tests`
- `git diff --check`
