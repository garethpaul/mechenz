# AGENTS.md

## Repository purpose

`garethpaul/mechenz` is a Python scraper and email notification sample. It polls a form-backed page, caches the latest scraped action list in memcache, and sends an SMTP notification when the data changes.

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `tests` - tests and fixtures
- `requirements.txt` - Python runtime dependencies

## Development commands

- Install dependencies: `python3 -m pip install -r requirements.txt`
- Full baseline: `make check`
- Lint/static checks: `make lint`
- Tests: `make test`
- Build: `make build`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Python.
- Prefer dependency-free tests or stdlib checks when legacy packages are unavailable.

## Testing guidance

- Test-related files detected: `tests/`, `tests/test_main.py`, `tests/test_royal_mail.py`, `tests/test_royalmail.py`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- Keep `settings.py`, SMTP credentials, target-site secrets, `.env` files, logs, and scraped private data out of git.
- Use `settings.py.example` only as a placeholder template with fake values.
- Scrape settings validation rejects blank job names, recipients, target sites, fake user agents, and fake referers before a live run.
- Scrape URL validation rejects non-HTTP(S) target and result URLs before a live run.
- SMTP numeric setting validation rejects invalid port and timeout values without echoing raw configuration values.
- SMTP recipient normalization strips recipient addresses and rejects all-blank recipient lists before opening SMTP connections.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
