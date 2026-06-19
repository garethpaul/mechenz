# Network Boundary Review

Status: in progress

## Scope

Review the maintained Python scraper stack through PR #17 together with the overlapping CI and bounded-response roots. Follow the call path from configured HTTP URLs through mechanize form submission and redirects, bounded response reading, HTML action parsing, memcache construction, SMTP STARTTLS, authentication, delivery, and cleanup.

## Findings

- A target page could supply a cross-origin form action, and mechanize redirects were accepted without checking the final response URL. That allowed a configured public target to steer the scraper toward an unintended HTTP(S) origin.
- Literal loopback/private targets, URL credentials, malformed ports, and request-header control characters passed initial scrape configuration validation.
- A response `close()` failure replaced the primary form-selection or response-read failure.
- Action containers had no explicit nesting budget even though response bytes were bounded.
- Memcache server strings were trimmed but not structurally parsed, so schemes, missing ports, invalid ports, and control characters reached the optional client.
- `SMTP.sendmail()` partial-refusal results were ignored, and `close()` failures replaced primary TLS/authentication/delivery errors.

## Fix Shape

- Restrict form actions and final response URLs to the explicitly configured HTTP(S) origins, reject unsafe authorities before live requests, and reject request-header controls.
- Keep the existing 15-second request timeout and 1 MiB total read budget, while adding a 256-level action-container nesting limit.
- Close HTTP and SMTP resources without masking an active primary exception.
- Parse memcache TCP endpoints before importing the client while preserving absolute Unix socket paths.
- Treat any SMTP recipient refusal as a delivery failure.
- Run offline fake HTTP/memcache/SMTP tests and isolated hostile source mutations.

## Verification

Pending final Python matrices, dependency audit, hosted checks, and merge reconciliation.

## Residual Risk

No live target site, redirect chain, DNS rebinding scenario, memcache server, SMTP provider, provider credentials, or real email delivery is exercised. Configured hostnames are treated as trusted operator input; the navigation policy prevents an already-opened page from changing to an unconfigured origin but does not pin DNS answers.
