# Security Policy

## Supported Versions

The supported security scope for `mechenz` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: No GitHub description is currently set.

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/mechenz` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be a public sample, documentation, or utility project. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Dependency manifests detected: `requirements.txt` and `constraints.txt`.
  Live-run dependency updates should preserve the compatibility ranges, the
  reviewed exact CI graph, and the offline `make check` path.
- Run `make check` before changing scraper parsing, SMTP delivery, dependency metadata, or settings documentation.
- The pinned Linux workflow uses a read-only, credential-free checkout,
  installs declared dependencies, and runs offline tests without target-site
  access, memcached connections, SMTP credentials, SMTP authentication, or
  email delivery.
- Prefer `SMTP_LOGIN` and `SMTP_PASSWORD` environment variables for SMTP credentials. Keep `settings.py`, SMTP credentials, target-site secrets, scraped private data, logs, and `.env` files out of git.
- Scrape settings validation should reject blank job names, recipients, target sites, fake user agents, and fake referers before a live run.
- Scrape URL validation should reject malformed or non-HTTP(S) target URLs before mechanize opens them.
- The scrape request timeout should bound the initial page, form submission,
  and optional result-page request so a remote endpoint cannot stall a run.
- Scrape encoding validation should reject unknown response codec names before live scraping without echoing raw configuration values.
- Nested action parser depth tests should use local response fixtures so
  container-shape regressions are detected without live scraping.
- SMTP numeric setting validation should restrict ports to `1..65535` and
  timeouts to finite values no greater than 300 seconds without echoing raw
  configuration values.
- SMTP recipient normalization should strip recipient addresses and reject all-blank recipient lists before opening outbound SMTP connections.
- SMTP header validation should reject CRLF in sender, recipient, and subject
  values before opening outbound SMTP connections.
- Robot setting validation should reject ambiguous `respect_robots` and `MECHENZ_IGNORE_ROBOTS` values without echoing raw configuration values.
- Tests should use injected fakes and local fixtures rather than live scraping, memcache, or SMTP.

## Service and API Notes

For web services, APIs, sockets, or scraping workflows, prioritize reports involving authentication bypass, authorization errors, injection, server-side request forgery, unsafe deserialization, credential leakage, data exposure, or denial-of-service conditions. Use test accounts and minimal proof-of-concept traffic only.

For this project, reports should also describe whether scrape settings validation, scrape encoding validation, robot setting validation, target-site terms, cache keys, or outbound email delivery could expose credentials or scraped private data.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep manifests in sync when they exist. Do not commit credentials, private keys, tokens, generated secrets, scraped private data, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

GitHub Actions applies `constraints.txt` to freeze the reviewed Python 3.12
resolution. This reduces resolver drift but is not artifact authentication;
the constraints file does not contain package hashes.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
