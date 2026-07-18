# Changes

## 2026-07-18 - P2 - Pin the scrape bounds by value, not by spelling

- Summary: the scrape request timeout and response body limit were pinned only
  as source text, while every test sized its fixtures from the constants
  themselves, so widening either bound passed the whole gate at exit 0.
- Files: added two literal boundary regressions to `tests/test_main.py`, added
  the matching widening mutations to `scripts/test-security-mutations.py`, and
  pinned the new regressions and their literals in `scripts/check-baseline.py`.
- Tests: both new regressions fail before the fix and pass after; `make check`
  now runs 55 offline tests and rejects ten hostile mutations. Measured on the
  base commit: widening `MAX_SCRAPE_RESPONSE_BYTES` to 1 GiB and
  `SCRAPE_REQUEST_TIMEOUT` to 1500s both exited 0, while rewriting the same
  values as `1048576` and `0xF` were rejected.
- Findings: `MAX_MEMCACHE_TIMEOUT`, `DEFAULT_MEMCACHE_TIMEOUT`,
  `MAX_ACTION_DIV_NESTING`, and the SMTP port/timeout maxima already probe at
  the boundary with literals (`"301"`, `5.0`, `"<div>" * 300`, `"65536"`) and
  correctly caught widening; only these two bounds lacked that coverage.
- Blockers: `mechanize` and `python-memcached` are not installed in the audit
  sandbox; the offline suite is standard-library only and passed regardless. No
  live network, SMTP, or memcache validation was performed.
- Next action: none; the mutation harness now proves both bounds gate.

## 2026-06-26 15:13 PDT - P1 - Preserve successful SMTP delivery

- Summary: stopped final SMTP close failures from reclassifying an already
  accepted message as failed and causing duplicate retry notifications.
- Files: tightened `RoyalMail.py`, added a fake SMTP regression, expanded the
  mutation suite, and documented the SMTP delivery cleanup contract.
- Tests: the new success-path cleanup regression failed before implementation;
  Python 3.11/3.12 passed all 53 offline tests, eight hostile mutations, root
  and external `make check`, syntax compilation, strict Git validation,
  generated-artifact checks, and secret/conflict scans.
- Findings: primary-error cleanup was protected, but successful delivery used an
  unguarded `close()` whose transport error escaped before cache update.
- Blockers: Codex review may remain unavailable because prior attempts return
  HTTP 401; skip after one attempt if unchanged.
- Next action: open the focused PR, attempt Codex review once, and merge only an
  exact hosted-green head.

## 2026-06-21

- Corrected trusted-root discovery when an inert absolute `-f` input precedes
  a relative repository `Makefile`.

- Made absolute external Makefile invocations work when checkout paths contain
  spaces or a literal apostrophe while rejecting `ROOT` and `MAKEFILE_LIST`
  attempts to redirect verification.
- Hardened the hosted `make check` entrypoint so a later duplicate
  `override ROOT` cannot redirect recipes before the real policy runs; rejected
  `MAKEFILES`, ignored caller `SHELL`, and documented extra makefiles as
  caller-supplied code.

## 2026-06-19

- Restricted mechanize form actions and final redirects to configured HTTP(S)
  origins, rejected unsafe authorities and request-header controls, and bounded
  action-container nesting.
- Preserved primary HTTP and SMTP failures when cleanup also fails, rejected
  partial SMTP recipient refusals, and structurally validated memcache endpoints.
- Added fake-network regression coverage and seven isolated hostile mutations.

## 2026-06-17

- Added a bounded memcache socket timeout with a 5-second default, validated
  environment/settings overrides, and sanitized invalid-value failures.

## 2026-06-16

- Added SMTP STARTTLS certificate verification with Python's default client TLS
  context before authentication.

## 2026-06-15

- Closed landing-page responses before form submission and on form-preparation failures.
- Added scrape short-read handling so partial response reads are accumulated
  without exceeding the existing response-size budget.
- Added deterministic scrape response closure for replaced, completed, and
  failed bounded reads.

## 2026-06-14

- Added a 1 MiB scrape response body limit before decoding and action parsing.
- Added memcache server normalization so single strings remain one endpoint and
  blank or unsupported collections fail before client construction.
- Added a 15-second scrape request timeout to every mechanize network open,
  including form submission.

## 2026-06-13

- Made tests, compilation, static checks, formatting checks, and generated-file
  cleanup resolve from the checkout for absolute Makefile invocations.
- Corrected nested action parser depth so ordinary inner containers cannot
  end an action before its first span is read.

## 2026-06-12

- Stopped the hosted checkout from persisting its credential and added an exact
  static contract for the sole workflow, permissions, and checkout step.

## 2026-06-10

- Added a reviewed five-package Python 3.12 constraints graph for hosted
  dependency resolution, with exact workflow, cache, documentation, and plan
  contracts. Version constraints do not authenticate package artifacts.
- Bounded SMTP ports to `1..65535` and SMTP timeouts to finite values no
  greater than 300 seconds.
- Added pinned, read-only Python 3.12 hosted validation for dependency
  installation, `pip check`, and the offline canonical gate.
- Added scrape encoding validation so unknown response codecs fail before live
  scraping without echoing raw configuration values.

## 2026-06-09

- Added local `make lint` and `make build` gate targets alongside `make test`
  and `make check` for the Python scraper baseline.
- Added scrape URL validation so malformed or non-HTTP(S) target URLs fail
  before live scraping.
- Added SMTP recipient normalization so blank recipient lists fail before an
  SMTP connection is opened.
- Added SMTP header validation so CRLF in sender, recipient, or subject values
  fails before an SMTP connection is opened.
- Added robot setting validation so ambiguous `respect_robots` or
  `MECHENZ_IGNORE_ROBOTS` values fail closed without echoing raw values.

## 2026-06-08

- Ported the scraper and SMTP helper to Python 3-compatible imports and syntax.
- Added runtime-only imports for optional live dependencies so tests can run without mechanize, memcache, or live SMTP.
- Added environment-backed SMTP configuration with an ignored `settings.py` compatibility fallback.
- Added scrape settings validation for blank live-run target, recipient, user-agent, and referer values.
- Added SMTP numeric setting validation that rejects invalid port and timeout values without echoing raw configuration.
- Added parser, cache, notification, and SMTP unit tests using the Python standard library.
- Added dependency metadata and `make check` verification.
