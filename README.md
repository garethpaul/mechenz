# mechenz

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/mechenz` is a Python scraper and email notification sample. It polls a form-backed page, caches the latest scraped action list in memcache, and sends an SMTP notification when the data changes.

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Python.

## Repository Contents

- `README.md` - project overview and local usage notes
- `CHANGES.md` - recent maintenance changes
- `Makefile` - local verification entry point
- `RoyalMail.py` - SMTP notification helper
- `main.py` - scraper, parser, cache comparison, and notification flow
- `requirements.txt` - live-run dependency metadata
- `settings.py.example` - local settings template without secrets
- `tests` - offline unit tests for parsing, cache comparison, and SMTP setup
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source files: main.py, RoyalMail.py
- Dependency and build manifests: Makefile, requirements.txt
- Entry points or build surfaces: `make check`, main.py
- Test-looking files: tests/test_main.py, tests/test_royal_mail.py, tests/test_royalmail.py

## Getting Started

### Prerequisites

- Git
- Python 3.10 or newer
- Optional for live polling: memcached and the packages in `requirements.txt`

### Setup

```bash
git clone https://github.com/garethpaul/mechenz.git
cd mechenz
make check
cp settings.py.example settings.py
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Install live-run dependencies when you are ready to poll a real site:

```bash
python3 -m pip install -r requirements.txt
```

- Fill in `settings.py` locally, start memcached, export SMTP credentials, and run:

```bash
export SMTP_LOGIN="sender@example.com"
export SMTP_PASSWORD
python3 main.py
```

## Testing and Verification

- `make check` compiles the Python modules and runs `python3 -m unittest discover -s tests`.
- The tests do not require mechanize, memcache, SMTP credentials, Gmail, a target site, or a private `settings.py`.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- Keep `settings.py`, SMTP credentials, target-site secrets, `.env` files, logs, and scraped private data out of git.
- Use `settings.py.example` only as a placeholder template with fake values.
- Scrape settings validation rejects blank job names, recipients, target sites, fake user agents, and fake referers before a live run.
- Scrape URL validation rejects non-HTTP(S) target and result URLs before a live run.
- SMTP numeric setting validation rejects invalid port and timeout values without echoing raw configuration values.
- SMTP recipient normalization strips recipient addresses and rejects all-blank recipient lists before opening SMTP connections.
- Prefer `SMTP_LOGIN` and `SMTP_PASSWORD` environment variables for SMTP credentials; `settings.py` SMTP fields exist only for local compatibility.
- Keep `respect_robots = True` unless target-site access rules are documented.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include RoyalMail.py.
- Review changes that scrape live sites, disable robot handling, store scraped data, or send email.
- Keep scrape settings validation in place so blank target or recipient settings fail before live scraping or email delivery.
- Keep scrape URL validation in place so malformed or non-HTTP(S) targets fail before mechanize opens them.
- Tests should use fixtures and injected fakes, not live target sites, memcache, or SMTP.

## Maintenance Notes

- Run `make check` before pushing scraper, parser, mailer, dependency, settings-template, or documentation changes.
- See `docs/plans/2026-06-08-mechenz-baseline.md` for the current baseline plan.
- See `docs/plans/2026-06-09-mail-settings-validation.md` for the SMTP numeric setting validation guard.
- See `docs/plans/2026-06-09-scrape-url-validation.md` for the scrape URL validation guard.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
