# AGENTS.md

## Repository purpose

`garethpaul/mechenz` is a Python scraper and email notification sample. It polls a form-backed page, caches the latest scraped action list in memcache, and sends an SMTP notification when the data changes.

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `tests` - tests and fixtures
- `requirements.txt` - Python runtime dependency ranges
- `constraints.txt` - reviewed hosted dependency resolution

## Development commands

- Install dependencies: `python3 -m pip install -r requirements.txt -c constraints.txt`
- Full baseline: `make check`
- Lint/static checks: `make lint`
- Tests and hostile mutations: `make test`
- Build: `make build`

## Coding conventions

- Keep live network dependencies behind injected factories so offline tests remain deterministic.
- Prefer standard-library tests when legacy optional packages are unavailable.
- Validate configuration before importing or constructing optional live clients.

## Testing guidance

- Start with the narrowest relevant test, then run `make check` before handoff.
- Keep hostile fake HTTP, memcache, and SMTP coverage for network-boundary changes.
- Keep README verification notes synchronized with commands and supported toolchains.

## PR / change guidance

- Keep diffs focused and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests and documentation when behavior or security boundaries change.
- Call out skipped live-service validation and legacy toolchain assumptions.

## Safety and gotchas

- Keep `settings.py`, SMTP credentials, target-site secrets, `.env` files, logs, and scraped private data out of git.
- Use `settings.py.example` only as a placeholder template with fake values.
- Preserve HTTP(S) navigation validation, redirect-origin checks, finite network timeouts, bounded response reads, memcache endpoint validation, and verified SMTP STARTTLS.
- Preserve SMTP delivery cleanup semantics: primary send failures surface, but
  close errors after an accepted message must not trigger duplicate retries.
- Do not weaken the read-only, credential-free hosted checkout.

## Agent workflow

1. Inspect the README, Makefile, manifests, and files directly related to the request.
2. Reproduce concrete defects with the narrowest failing test before changing production code.
3. Make the smallest source or docs change that establishes the invariant.
4. Run the narrow test, hostile mutations, then `make check` and supported Python matrices.
5. Record unavailable credentials, providers, devices, or live-network validation.
