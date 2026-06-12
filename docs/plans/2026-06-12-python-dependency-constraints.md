---
title: Python Dependency Constraints
date: 2026-06-12
status: completed
execution: code
---

## Context

`requirements.txt` intentionally declares compatible mechanize and
python-memcached ranges, but GitHub Actions previously resolved those ranges
and every transitive dependency afresh. Python 3.12 currently selects a stable
five-package graph that can be reviewed and frozen without narrowing the
sample's direct compatibility declarations.

## Goals

- Preserve the direct dependency ranges in `requirements.txt`.
- Add one reviewed constraints file for the complete Python 3.12 graph.
- Install through the constraints file in GitHub Actions and invalidate the
  pip cache when either dependency file changes.
- Make the dependency-free checker reject graph drift, unconstrained hosted
  installs, cache-key drift, documentation drift, and incomplete plan evidence.
- Document that version constraints do not authenticate package artifacts.

## Scope Boundaries

- Do not change scraper, cache, SMTP, or configuration behavior.
- Do not narrow the direct compatibility ranges in `requirements.txt`.
- Do not claim hash-locked or offline-reproducible installation.
- Do not merge or close existing pull requests without authorization.

## Work Completed

- Added the exact five-package graph selected for Python 3.12.
- Applied the graph to hosted installation and included both dependency files
  in setup-python's pip cache key.
- Extended the dependency-free checker with exact dependency, workflow,
  documentation, and completed-plan contracts.
- Updated setup, security, and change guidance without changing runtime code.

## Verification Completed

- Official PyPI metadata verified non-yanked release artifacts for
  mechanize 0.4.10, python-memcached 1.62, html5lib 1.1, six 1.17.0, and
  webencodings 0.5.1.
- A Python 3.12 resolver dry run selected that exact five-package graph.
- An isolated Python 3.12.8 environment installed through `requirements.txt`
  and `constraints.txt`; with the inherited `PYTHONPATH` removed,
  `python -m pip check` reported no broken requirements.
- `make check`, `make lint`, `make test`, and `make build` passed with all 23
  offline tests, static checks, and Python compilation successful.
- Ten focused mutations were rejected across constraint version drift, graph
  removal or addition, direct-range drift, unconstrained or duplicate installs,
  cache-key drift, documentation drift, status regression, and lost PyPI
  evidence.
- `python3 -m py_compile scripts/check-baseline.py` and `git diff --check`
  passed.
- Implementation head `63e91f82cbebd09e26770d820c942f7f03814c93`
  passed push Check run `27437261487`, pull-request Check run `27437266988`,
  and CodeQL run `27437265086` for Actions and Python.
- Pull request #6 was open, clean, and mergeable at that implementation head
  with all five exact-head checks successful and zero open PR-scoped
  code-scanning alerts.
